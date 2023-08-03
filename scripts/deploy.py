import sys
import time
import math
import warnings
warnings.filterwarnings('ignore')
sys.path.append('pytorchvideo')
sys.path.append('scripts')

from pytorchvideo.data.encoded_video import EncodedVideo
import torch
import numpy as np
import multiprocessing

from pytorchvideo.transforms import (
    ApplyTransformToKey, 
    UniformTemporalSubsample,
    RandomShortSideScale,
)

from torchvision.transforms import (
    functional as F,
    Compose,
)

from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)

from model import VideoClassifier

seed = 0
import random, os

random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = True

pred_legend = {
    0: 'Correct',
    1: 'Unmoving',
    2: 'Incorrect',
    3: 'Unsure'
}
time_start = time.time()
class multiThreadedVideoPredictor:
    def __init__(self, num_workers=4):
        self._num_workers = num_workers
        
        self._model = VideoClassifier()
        self._model.load_state_dict(torch.load('model.pth'))
        self._model.eval()
        
        self._video_transform = Compose([
            ApplyTransformToKey(key = 'video',
            transform = Compose([
                UniformTemporalSubsample(20),
                NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
                RandomShortSideScale(min_size=256, max_size=320),
                CenterCropVideo(224),
            ])),
        ])
        
        self._waiting_queue = multiprocessing.Queue()
        self._result_dict = multiprocessing.Manager().dict()
        
        self._processes = []
        
        self.spawn_workers(self._num_workers)
            
    def spawn_workers(self, num_workers:int):
        for i in range(num_workers):
            p = self.prediction_worker(self._waiting_queue, self._result_dict, self._video_transform, self._model, i)
            p.start()
            self._processes.append(p)
            
    def kill_workers(self):
        for i in self._processes:
            self._waiting_queue.put(None)
    
    def predict_video(self, video_path):
        p = self.prep_worker(self._waiting_queue, self._result_dict, video_path)
        p.start()
        
    def get_progress(self, video_path):
        if video_path not in self._result_dict:
            return 0
        return len(self._result_dict[video_path]['preds'])/self._result_dict[video_path]['total_preds']*100
    
    def get_result(self, video_path):
        # return self._result_dict[video_path]['preds']
        
        softmax_preds = {x['timestamp']: [round(prob, 2) for prob in x['pred']] for x in self._result_dict[video_path]['preds']}
        sorted_softmax_preds = dict(sorted(softmax_preds.items()))
        preds = [np.argmax(x) for x in sorted_softmax_preds.values()]
        entropy = [round(self.calculate_entropy(x), 1) for x in sorted_softmax_preds.values()]
        for i, e in enumerate(entropy):
            if e > 0.6:
                preds[i] = 3
        final_preds = [pred_legend[x] for x in preds]
        
        # video is labeled as correct if there are more than 10s or 80% of the video is labeled as correct, whichever is smaller
        # video is labeled as incorrect if there are more than 4s or 40% of the video is labeled as incorrect, whichever is smaller
        # video is labeled as incorrect if more than 60% of the video is labeled as unmoving
        # video is labeled as unsure if more than 30% of the video is labeled as unsure
        
        if preds.count(3) > 0.3*len(preds):
            overall_pred = 'Unsure'
        elif preds.count(1) > 0.6*len(preds):
            overall_pred = 'Incorrect'
        elif preds.count(2) > 0.4*len(preds) or preds.count(2) > 2:
            overall_pred = 'Incorrect'
        elif preds.count(0) > 0.8*len(preds) or preds.count(0) > 5:
            overall_pred = 'Correct'
        else:
            overall_pred = 'Unsure'
            
        return {
            'softmax_preds': sorted_softmax_preds,
            'final_preds': final_preds,
            'overall_pred': overall_pred,
            'entropy': entropy,
        }
        
    def remove_entry(self, video_path):
        try:
            self._result_dict.pop(video_path)
        except:
            pass
        
    def calculate_entropy(self, softmax_preds):
        entropy = 0
        for p in softmax_preds:
            if p > 0:
                entropy += -p * math.log2(p)
        return entropy
        
            
    class prep_worker(multiprocessing.Process):
        def __init__(self, waiting_queue, result_dict, video_path):
            super().__init__()
            self._waiting_queue = waiting_queue
            self._result_dict = result_dict
            self._video_path = video_path
            
        def run(self):
            self._video = EncodedVideo.from_path(self._video_path)
            for timestamp in range(self._video.duration//2):
                self._waiting_queue.put({
                    'timestamp': timestamp*2,
                    'video_path': self._video_path,
                })
            self._result_dict[self._video_path] = {
                'total_preds': self._video.duration//2,
                'preds': [],
            }
            
    class prediction_worker(multiprocessing.Process):
        def __init__(self, queue, result_dict, video_transform, model, worker_id):
            super().__init__()
            self._queue = queue
            self._result_dict = result_dict
            self._worker_id = worker_id
            self._video_transform = video_transform
            self._model = model
            self._video_path = None
            
        def run(self):
            while True:
                task = self._queue.get()
                if task == None:
                    break
                else:
                    if self._video_path != task['video_path']:
                        self._video_path = task['video_path']
                        self._video = EncodedVideo.from_path(self._video_path)
                        
                    clip = self._video.get_clip(start_sec=task['timestamp'], end_sec=task['timestamp']+2)
                    transformed_clip = self._video_transform(clip)
                    inputs = transformed_clip['video'].unsqueeze(0)
                    pred = self._model(inputs).detach().cpu().numpy().flatten()
                    updated_preds = self._result_dict[task['video_path']]
                    updated_preds['preds'].append({
                        'pred': pred,
                        'timestamp': task['timestamp'],
                    })
                    self._result_dict[task['video_path']] = updated_preds
                        
    
if __name__ == '__main__':
    video_path = r"Zedong_fullTitration_1.mp4"
    predictor = multiThreadedVideoPredictor()
    start_time = time.time()
    predictor.predict_video(video_path)
    progress = 0
    while progress < 100:
        time.sleep(1)
        new_progress = predictor.get_progress(video_path)
        if progress != new_progress:
            progress = new_progress
            print(f'progress: {progress}%')
    results = predictor.get_result(video_path)
    print('overall prediction:', results['overall_pred'])
    for i, softmax, pred, entropy in zip(range(len(results['softmax_preds'])), results['softmax_preds'], results['final_preds'], results['entropy']):
        print(f'{i*2}-{i*2+2}s: {pred} {list(softmax["pred"])} {entropy}')
    print('time taken:', time.time()-start_time)
    predictor.kill_workers()