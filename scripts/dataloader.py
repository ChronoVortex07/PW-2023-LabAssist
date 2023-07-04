import sys
sys.path.append('pytorchvideo')

from pytorchvideo.data import make_clip_sampler, labeled_video_dataset
from torch.utils.data import DataLoader

from pytorchvideo.transforms import (
    ApplyTransformToKey, 
    RandomShortSideScale,
    UniformTemporalSubsample,
    
)

from torchvision.transforms import (
    functional as F,
    Compose,
    RandomHorizontalFlip,
)

from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
class train_dataloader(DataLoader):
    def __init__(self, dataset_df, batch_size, num_workers):
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
        dataset = labeled_video_dataset(
            dataset_df,
            clip_sampler=make_clip_sampler('random', 2),
            transform=video_transform,
            decode_audio=False,
        )
        super().__init__(dataset, batch_size=batch_size, num_workers=num_workers, pin_memory=True)
        
class test_dataloader(DataLoader):
    def __init__(self, dataset_df, batch_size, num_workers):
        video_transform = Compose([
        ApplyTransformToKey(key = 'video',
            transform = Compose([
                # UniformTemporalSubsample(20),
                # NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
                # CenterCropVideo(224),
                UniformTemporalSubsample(20),
                NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
                RandomShortSideScale(min_size=256, max_size=320),
                CenterCropVideo(224),
            ])),
        ])
        dataset = labeled_video_dataset(
            dataset_df,
            clip_sampler=make_clip_sampler('random', 2),
            transform=video_transform,
            decode_audio=False,
        )
        super().__init__(dataset, batch_size=batch_size, num_workers=num_workers, pin_memory=True)