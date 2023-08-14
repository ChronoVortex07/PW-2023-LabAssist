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
    Lambda,
)

from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
import numbers

def divide_by_255(tensor):
    return tensor / 255.0
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
class train_dataloader(DataLoader):
    def __init__(self, dataset_df, batch_size, num_workers):
        video_transform = Compose([
            ApplyTransformToKey(key = 'video',
            transform = Compose([
                UniformTemporalSubsample(20),
                Lambda(divide_by_255),
                NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
                RandomShortSideScale(min_size=256, max_size=320),
                # CenterCropVideo(224),
                BottomCropVideo(224),
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
                UniformTemporalSubsample(20),
                Lambda(divide_by_255),
                NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
                RandomShortSideScale(min_size=256, max_size=320),
                # CenterCropVideo(224),
                BottomCropVideo(224),
            ])),
        ])
        dataset = labeled_video_dataset(
            dataset_df,
            clip_sampler=make_clip_sampler('random', 2),
            transform=video_transform,
            decode_audio=False,
        )
        super().__init__(dataset, batch_size=batch_size, num_workers=num_workers, pin_memory=True)