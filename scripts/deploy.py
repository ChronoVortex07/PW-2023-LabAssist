import sys
import time
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

pred_legend = {
    0: 'Correct',
    1: 'Unmoving',
    2: 'Incorrect',
}
time_start = time.time()
class multiThreadedVideoPredictor(object):
        def __init__(self, model, video_transform, num_workers=4):
            self.num_workers = num_workers
            self.model = model
            self.video_transform = video_transform
        
        # def predict_video(self, video_path):
        #     process_pool = multiprocessing.Pool(self.num_workers)
        #     video = EncodedVideo.from_path(video_path)
        #     output = process_pool.map(self.predict_clip, enumerate([video_path] * (video.duration//2)))
        #     process_pool.close()
        #     process_pool.join()
        #     preds = np.array([x['pred'] for x in output])
        #     mean_softmax = np.mean(preds, axis=0)
        #     return {'pred': preds, 'pred_legend': pred_legend[np.argmax(mean_softmax)]}
        
        def predict_video(self, video_path):
            self.queue = multiprocessing.Queue()
            self.result_queue = multiprocessing.Queue()
            
            self.processes = []
            
            video = EncodedVideo.from_path(video_path)
            for timestamp in range(video.duration//2):
                self.queue.put(timestamp*2)
            self.total_tasks = self.queue.qsize()
            for _ in range(self.num_workers):
                self.queue.put(None)
            for i in range(self.num_workers):
                
                # p = multiprocessing.Process(target=self.asyncClipPrediction, args=(self.queue, self.result_queue, video_path, i))
                p = self.Worker(self.queue, self.result_queue, video_path, self.video_transform, self.model, i)
                p.start()
                self.processes.append(p)
        
        def get_progress(self):
            return int(self.result_queue.qsize()/(self.total_tasks)*100)
        
        def get_result(self):
            if self.result_queue.empty():
                return None
            else:
                results = []
                while not self.result_queue.empty():
                    results.append(self.result_queue.get())
                return results
                
        class Worker(multiprocessing.Process):
            def __init__(self, queue, result_queue, video_path, video_transform, model, worker_id):
                super().__init__()
                self.queue = queue
                self.result_queue = result_queue
                self.video_path = video_path
                self.worker_id = worker_id
                self.video_transform = video_transform
                self.model = model
                
            def run(self):
                while True:
                    task = self.queue.get()
                    if task == None:
                        break
                    else:
                        time.sleep(0.1)
                        video = EncodedVideo.from_path(self.video_path)
                        clip = video.get_clip(start_sec=task, end_sec=task+2)
                        transformed_clip = self.video_transform(clip)
                        inputs = transformed_clip['video'].unsqueeze(0)
                        pred = self.model(inputs).detach().cpu().numpy().flatten()
                        self.result_queue.put({
                            'pred': pred,
                            'timestamp': task,
                        })
                        progress = int(self.result_queue.qsize()/(self.queue.qsize()+self.result_queue.qsize())*100)
                
def predict_video(video_path):  
    video_transform = Compose([
        ApplyTransformToKey(key = 'video',
        transform = Compose([
            UniformTemporalSubsample(20),
            NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
            RandomShortSideScale(min_size=256, max_size=320),
            CenterCropVideo(224),
        ])),
    ])
    
    model = VideoClassifier()
    model.load_state_dict(torch.load('model.pth'))
    model.eval()

    predictor = multiThreadedVideoPredictor(
        model, 
        video_transform, 
        num_workers=4)

    predictor.predict_video(video_path)
    return predictor
    # print('prediction:', output['pred_legend'])
    
if __name__ == '__main__':
    predictor = predict_video(r"C:\Users\zedon\Videos\PW2023VIDEOS\Test\Unmoving\Zedong_Clear_Unmoving_2.mp4")
    while predictor.get_progress() < 100:
        time.sleep(1)
    results = predictor.get_result()
    preds = np.array([x['pred'] for x in results])
    mean_softmax = np.mean(preds, axis=0)
    print('prediction:', pred_legend[np.argmax(mean_softmax)])