import sys
sys.path.append('pytorchvideo')

from pytorchvideo.data.encoded_video import EncodedVideo
import torch
import pandas as pd
import numpy as np

from pytorchvideo.transforms import (
    ApplyTransformToKey, 
    RandomShortSideScale,
    UniformTemporalSubsample,
)

from torchvision.transforms import (
    Compose,
    RandomHorizontalFlip,
)

from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)

from model import VideoClassifier
from dataloader import video_dataloader

pred_legend = {
    0: 'Correct',
    1: 'Unmoving',
    2: 'Incorrect',
}

video_transform = Compose([
    ApplyTransformToKey(key = 'video',
    transform = Compose([
        UniformTemporalSubsample(20),
        NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
        RandomShortSideScale(min_size=256, max_size=320),
        CenterCropVideo(224),
        RandomHorizontalFlip(p=0.5),
    ])),
])


train_df = pd.read_csv('train.csv')
val_df = pd.read_csv('test.csv')
model = VideoClassifier(train_df, val_df, video_dataloader)
model.load_state_dict(torch.load('model.pth'))
model.eval()

video = EncodedVideo.from_path('Zedong_fullTitration_2.mp4')
preds = []
for i in range(int(video.duration//2)):
    video_data = video.get_clip(start_sec=i+1, end_sec=i+3)
    video_data = video_transform(video_data)
    inputs = video_data['video'].unsqueeze(0)

    pred = model(inputs).detach().cpu().numpy()
    preds.append(pred)
# average softmax
average_softmax = np.mean(preds, axis=0)
print('prediction:', pred_legend[np.argmax(average_softmax)])

