import sys
import time
import math
import warnings
warnings.filterwarnings('ignore')
sys.path.append('pytorchvideo')
sys.path.append('scripts')

from pytorchvideo.data.encoded_video import EncodedVideo
from collections import Counter
import torch
import numpy as np
import multiprocessing
import numbers
import cv2

from pytorchvideo.transforms import (
    ApplyTransformToKey, 
    UniformTemporalSubsample,
    RandomShortSideScale,
    Normalize,
)

from torchvision.transforms import (
    functional as F,
    Compose,
    Lambda,
)

from app.scripts.RelativePosition import rel_pos
from app.scripts.model import VideoClassifier
from ultralytics.models.yolo import YOLO

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

def divide_by_255(x):
    return x/255.0

class BottomCropVideo:
    def __init__(self, crop_size):
        if isinstance(crop_size, numbers.Number):
            self.crop_size = (int(crop_size), int(crop_size))
        else:
            self.crop_size = crop_size

    def __call__(self, clip):
        """
        Args:
            clip (torch.tensor): Video clip to be cropped. Size is (C, T, H, W)
        Returns:
            torch.tensor: central cropping of video clip. Size is
            (C, T, crop_size, crop_size)
        """
        if clip.shape[2] < clip.shape[3]:
            cropped_clip = F.crop(clip, 0, 0, clip.shape[2], clip.shape[2])
        else:
            cropped_clip = F.crop(clip, clip.shape[2] - clip.shape[3], 0, clip.shape[3], clip.shape[3])
        return F.resize(cropped_clip, self.crop_size, interpolation=F.InterpolationMode.BILINEAR)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(crop_size={self.crop_size})"
class multiThreadedVideoPredictor:
    def __init__(self, num_workers=4):
        self._num_workers = num_workers
        
        self._action_model = VideoClassifier()
        self._action_model.load_state_dict(torch.load('app/models/action_model_v2.pt'))
        self._action_model.eval()
        
        self._object_model = YOLO("app/models/object_model_v2.pt")
        
        self._video_transform = Compose([
            ApplyTransformToKey(key = 'video',
            transform = Compose([
                UniformTemporalSubsample(20),
                Lambda(divide_by_255),
                Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
                RandomShortSideScale(min_size=256, max_size=320),
                BottomCropVideo(224),
            ])),
        ])
        
        self._waiting_queue = multiprocessing.Queue()
        self._result_dict = multiprocessing.Manager().dict()
        
        self._processes = []
        
        self.spawn_workers(self._num_workers)
            
    def spawn_workers(self, num_workers:int):
        for i in range(num_workers):
            p = self.prediction_worker(self._waiting_queue, self._result_dict, self._video_transform, self._action_model, self._object_model, i)
            p.start()
            self._processes.append(p)
            
    def kill_workers(self, num_workers:int=None):
        if num_workers is None:
            num_workers = self._num_workers
        for _ in range(num_workers):
            self._waiting_queue.put(None)
            
    def update_workers(self, num_workers:int):
        if num_workers > self._num_workers:
            self.spawn_workers(num_workers-self._num_workers)
        elif num_workers < self._num_workers:
            self.kill_workers(self._num_workers-num_workers)
        self._num_workers = num_workers
        
    def get_num_workers(self):
        return self._num_workers
    
    def predict_video(self, video_path):
        if self.get_progress(video_path) > 0 and self.get_progress(video_path) < 100:
            print('prediction already in progress')
            return
        if self.get_progress(video_path) == 100:
            self.remove_entry(video_path)
        p = self.prep_worker(self._waiting_queue, self._result_dict, video_path)
        p.start()
        
    def get_progress(self, video_path):
        if video_path not in self._result_dict:
            return 0
        if self._result_dict[video_path]['yolo_pred'] == None:
            yolo_progress = 0
        else:
            yolo_progress = 1
        return (len(self._result_dict[video_path]['flask_preds'])+yolo_progress)/self._result_dict[video_path]['total_preds']*100
    
    def get_result(self, video_path):
        softmax_preds = {x['timestamp']: [round(prob, 2) for prob in x['flask_pred']] for x in self._result_dict[video_path]['flask_preds']}
        sorted_softmax_preds = dict(sorted(softmax_preds.items()))
        flask_preds = [np.argmax(x) for x in sorted_softmax_preds.values()]
        entropy = [round(self.calculate_entropy(x), 1) for x in sorted_softmax_preds.values()]
        yolo_pred = self._result_dict[video_path]['yolo_pred']

        # Idk why sometimes yolo_pred is None but it is
        if yolo_pred == None:
            yolo_pred = {
                'white_tile_present': None,
                'funnel_present': None,
                'burette_too_high': None,
            }
        
        for i, e in enumerate(entropy):
            if e > 0.6:
                flask_preds[i] = 3
        final_preds = [pred_legend[x] for x in flask_preds]
        
        # video is labeled as correct if there are more than 10s or 80% of the video is labeled as correct, whichever is smaller
        # video is labeled as incorrect if there are more than 4s or 40% of the video is labeled as incorrect, whichever is smaller
        # video is labeled as incorrect if more than 60% of the video is labeled as unmoving
        # video is labeled as unsure if more than 30% of the video is labeled as unsure
        # video is labeled as incorrect if funnel is present, white tile is not present or burette is too high while correct or incorrect swirling is occuring
        
        if flask_preds.count(3) > 0.3*len(flask_preds):
            overall_pred = 'Unsure'
        elif flask_preds.count(1) > 0.6*len(flask_preds):
            overall_pred = 'Incorrect'
        elif flask_preds.count(2) > 0.4*len(flask_preds) or flask_preds.count(2) > 2:
            overall_pred = 'Incorrect'
        elif flask_preds.count(0) > 0.8*len(flask_preds) or flask_preds.count(0) > 5:
            overall_pred = 'Correct'
        else:
            overall_pred = 'Unsure'
            
        if yolo_pred['white_tile_present'] == False or yolo_pred['funnel_present'] == True or yolo_pred['burette_too_high'] == True:
            overall_pred = 'Incorrect'
            
        return {
            'softmax_preds': sorted_softmax_preds,
            'final_preds': final_preds,
            'overall_pred': overall_pred,
            'yolo_preds': yolo_pred,
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
            self._result_dict[self._video_path] = {
                'total_preds': self._video.duration//2+1,
                'flask_preds': [],
                'yolo_pred': None,
            }
            for timestamp in range(int(self._video.duration//2)):
                self._waiting_queue.put({
                    'type': 'action_detection',
                    'timestamp': timestamp*2,
                    'video_path': self._video_path,
                })
            self._waiting_queue.put({
                'type': 'object_detection',
                'timestamps': list(range(0, 4*self._video.duration//4, self._video.duration//4)),
                'video_path': self._video_path,
            })
            
            print('\n'+self._video_path+' added to queue')
            print('total preds:', self._video.duration//2+1)
            print('timestamps:', list(range(int(self._video.duration//2))))
            print('total tasks:', len(list(range(int(self._video.duration//2))))+1)
            
    class prediction_worker(multiprocessing.Process):
        def __init__(self, queue, result_dict, video_transform, action_model, object_model, worker_id):
            super().__init__()
            self._queue = queue
            self._result_dict = result_dict
            self._worker_id = worker_id
            self._video_transform = video_transform
            self._action_model = action_model
            self._object_model = object_model
            self._video_path = None
            
            
        def run(self):
            while True:
                task = self._queue.get()
                if task == None:
                    break
                elif task['type'] == 'action_detection':
                    if self._video_path != task['video_path']:
                        self._video_path = task['video_path']
                        self._video = EncodedVideo.from_path(self._video_path)
                        
                    clip = self._video.get_clip(start_sec=task['timestamp'], end_sec=task['timestamp']+2)
                    transformed_clip = self._video_transform(clip)
                    inputs = transformed_clip['video'].unsqueeze(0)
                    flask_pred = self._action_model(inputs).detach().cpu().numpy().flatten()
                    
                    updated_preds = self._result_dict[task['video_path']]
                    updated_preds['flask_preds'].append({
                        'flask_pred': flask_pred,
                        'timestamp': task['timestamp'],
                    })
                    self._result_dict[task['video_path']] = updated_preds
                    
                elif task['type'] == 'object_detection':
                    if self._video_path != task['video_path']:
                        self._video_path = task['video_path']
                        self._video = EncodedVideo.from_path(self._video_path)
                        
                    data = []
                        
                    for timestamp in task['timestamps']:
                    
                        first_image = self.get_image(task['video_path'], timestamp)
                        first_image = self.pad_and_resize(first_image, (640, 640))
                        
                        data.append(rel_pos(self._object_model, first_image))
                        
                    # Count occurrences of values for each key
                    counts = {}
                    for entry in data:
                        for key, value in entry.items():
                            if key not in counts:
                                counts[key] = Counter()
                            counts[key][value] += 1

                    # Determine the most common value for each key using argmax
                    average_preds = {}
                    for key, count in counts.items():
                        most_common_value = max(count, key=count.get)
                        average_preds[key] = most_common_value
                        
                    updated_preds = self._result_dict[task['video_path']]
                    updated_preds['yolo_pred'] = average_preds
                    self._result_dict[task['video_path']] = updated_preds
        def get_image(self, video_path, timestamp):
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_index = int(fps * timestamp)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            cap.release()
            cv2.destroyAllWindows()
            return frame
        
        def pad_and_resize(self, frame, target_size):
            original_height, original_width, _ = frame.shape

            # Calculate the padding size
            max_dim = max(original_height, original_width)
            pad_top = (max_dim - original_height) // 2
            pad_bottom = max_dim - original_height - pad_top
            pad_left = (max_dim - original_width) // 2
            pad_right = max_dim - original_width - pad_left

            # Pad the frame with zeros to make it a square
            padded_frame = cv2.copyMakeBorder(frame, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

            # Resize the padded frame to (640, 640, 3)
            desired_size = target_size
            resized_frame = cv2.resize(padded_frame, desired_size)
            return resized_frame
                        
    
if __name__ == '__main__':
    video_path =  r"C:\Users\zedon\Desktop\PW-samples\S5_incorrect.mp4" #r"Zedong_fullTitration_1.mp4" #
    predictor = multiThreadedVideoPredictor(2)
    start_time = time.time()
    predictor.predict_video(video_path)
    progress = 0
    while progress < 100:
        time.sleep(1)
        new_progress = predictor.get_progress(video_path)
        if progress != new_progress:
            progress = new_progress
            print('progress: {:00.0%}'.format(progress/100), end='\r')
    results = predictor.get_result(video_path)
    print('\noverall prediction:', results['overall_pred'], 'yolo prediction:', results['yolo_preds'])
    for i, pred in enumerate(zip(results['final_preds'], results['entropy'])):
        print('timestamp: {:02d}, prediction: {}, entropy: {}'.format(i, pred[0], pred[1]))

    print('time taken:', round(time.time()-start_time))
    predictor.kill_workers()