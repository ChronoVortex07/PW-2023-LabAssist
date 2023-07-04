import sys
import cv2
import time
import warnings
warnings.filterwarnings('ignore')
sys.path.append('pytorchvideo')

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

class bottomCrop(object):
    def __init__(self, height, width):
        self.height = int(height)
        self.width = int(width)

    def __call__(self, clip):
        w = clip.size(-1)
        return F.crop(clip, 0, w - self.width, self.height, self.width)
    
class multiThreadedVideoPredictor(object):
    def __init__(self, model, video_transform, num_workers=4):
        self.num_workers = num_workers
        self.model = model
        self.video_transform = video_transform
    
    def predict_video(self, video_path):
        process_pool = multiprocessing.Pool(self.num_workers)
        video = EncodedVideo.from_path(video_path)
        output = process_pool.map(self.predict_clip, enumerate([video_path] * (video.duration//2)))
        process_pool.close()
        process_pool.join()
        preds = np.array([x['pred'] for x in output])
        mean_softmax = np.mean(preds, axis=0)
        return {'pred': preds, 'pred_legend': pred_legend[np.argmax(mean_softmax)]}
        
    def predict_clip(self, video):
        timestamp, video_path = video
        video = EncodedVideo.from_path(video_path).get_clip(start_sec=timestamp*2, end_sec=timestamp*2+2)
        video_data = self.video_transform(video)
        inputs = video_data['video'].unsqueeze(0)
        pred = self.model(inputs).detach().cpu().numpy().flatten()
        return {'pred': pred, 'timestamp': timestamp}

if __name__ == '__main__':
    video_transform = Compose([
        ApplyTransformToKey(key = 'video',
        transform = Compose([
            UniformTemporalSubsample(20),
            NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
            CenterCropVideo(224),
            RandomShortSideScale(min_size=256, max_size=320),
            # bottomCrop(224, 224),
        ])),
    ])
    time_start = time.time()
    
    model = VideoClassifier()
    model.load_state_dict(torch.load('model.pth'))
    model.eval()

    predictor = multiThreadedVideoPredictor(
        model, 
        video_transform, 
        num_workers=8)

    output = predictor.predict_video('Zedong_fullTitration_2.mp4')
    print('prediction:', output['pred_legend'])
    print('total time: {:.2f} seconds'.format(time.time() - time_start))