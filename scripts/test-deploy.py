import sys
import math
import time
import warnings
warnings.filterwarnings('ignore')
sys.path.append('pytorchvideo')

from pytorchvideo.data.encoded_video import EncodedVideo
import torch
import numpy as np
import multiprocessing

from pytorchvideo.transforms import (
    UniformTemporalSubsample,
)

from torchvision.transforms import (
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

from torchvision.io.video import read_video

class VideoDataset(torch.utils.data.Dataset):
    def __init__(self, video_path, clip_length):
        self.clip_length = clip_length
        self.frames, self.audio, self.info = read_video(video_path, pts_unit="sec")
        
        self.stop_getitem = False
        
        self.transform = Compose([
            UniformTemporalSubsample(20),
            NormalizeVideo(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
            CenterCropVideo(224),
        ])
        print('init done, total_clips: ', len(self), 'clip_length: ', self.clip_length, 'video_fps: ', int(self.info["video_fps"]))

    def __getitem__(self, idx):
        if idx > len(self):
            raise StopIteration
        
        start_frame = int(idx * self.clip_length * self.info["video_fps"])
        end_frame = int(start_frame + self.clip_length * self.info["video_fps"])
        actual_duration = len(self.frames) / self.info["video_fps"] - start_frame / self.info["video_fps"]
        clip = self.frames[start_frame:end_frame]
        # Pad the clip if it is shorter than the clip length
        if actual_duration < self.clip_length:
            pad_frames = int((self.clip_length - actual_duration) * self.info["video_fps"])
            clip = torch.cat([clip, torch.zeros(pad_frames, *clip.shape[1:])], dim=0)  # Pad with zeros
            print('padded clip')
            
        num_frames = clip.shape[0]     
        # convert from THWC to CTHW
        clip = clip.permute([3, 0, 1, 2]).float()
        # Apply any necessary transformations to the clip
        clip = self.transform(clip)
        print('getitem done, idx: ', idx, 'num_frames: ', num_frames, 'clip.shape: ', clip.shape)
        return clip

    def __len__(self):
        num_clips = int(len(self.frames) / self.info['video_fps'] / self.clip_length)
        return num_clips

class VideoDataLoader(torch.utils.data.DataLoader):
    def __init__(self, video_path, clip_length, batch_size, num_workers):
        dataset = VideoDataset(video_path, clip_length)
        if batch_size > len(dataset):
            batch_size = len(dataset)
        super().__init__(dataset, batch_size=batch_size, num_workers=num_workers)

if __name__ == '__main__':
    time_start = time.time()
    
    preds = []
    
    model = VideoClassifier()
    model.load_state_dict(torch.load('model.pth'))
    model.eval()
    
    def predict_clip(model, clip):
        output = model(clip).detach().cpu().numpy()
        return output
    
    # Example usage
    video_path = "Zedong_fullTitration_1.mp4"
    clip_length = 2  # Length of each clip in seconds
    batch_size = 1
    num_workers = 0

    # Create the video data loader
    data_loader = VideoDataLoader(video_path, clip_length, batch_size, num_workers)


    process_pool = multiprocessing.Pool(8)
    output = process_pool.map(predict_clip, data_loader)
    process_pool.close()
    process_pool.join()
    preds = np.concatenate(output)
    mean_softmax = np.mean(preds, axis=0)

    print('prediction:', pred_legend[np.argmax(mean_softmax)])
    print('total time: {:.2f} seconds'.format(time.time() - time_start))
    
