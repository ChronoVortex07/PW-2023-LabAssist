import os
import sys

sys.path.append('pytorchvideo')

import pandas as pd

import torch
from pytorch_lightning import seed_everything, Trainer
from pytorch_lightning.callbacks import ModelCheckpoint, LearningRateMonitor

import warnings
warnings.filterwarnings('ignore')

seed_everything(0)
torch.set_float32_matmul_precision('medium')

from model import VideoClassifier
from dataloader import train_dataloader, test_dataloader

df = pd.read_csv('train.csv')

train_df = pd.read_csv('train.csv')
val_df = pd.read_csv('test.csv')

model = VideoClassifier(
    learning_rate = 1e-3,
    batch_size = 6,
    num_worker = 0
)

checkpoint_callback = ModelCheckpoint(
    monitor = 'val_loss',
    dirpath = 'checkpoints',
    filename = 'model-{epoch:02d}-{val_loss:.2f}',
    save_last=True
)
lr_monitor = LearningRateMonitor(logging_interval='epoch')

trainer = Trainer(
    max_epochs = 500,
    accelerator = 'gpu',
    devices = -1, #-1
    precision = '16-mixed', # 16
    accumulate_grad_batches = 2,
    enable_progress_bar = True,
    num_sanity_val_steps = 0,
    callbacks = [lr_monitor, checkpoint_callback],
)

if __name__ == '__main__':
    train_loader = train_dataloader(train_df, batch_size=6, num_workers=0)
    val_loader = test_dataloader(val_df, batch_size=6, num_workers=0)
    test_loader = test_dataloader(val_df, batch_size=6, num_workers=0)
    
    # trainer.fit(model, train_loader, val_loader, ckpt_path='checkpoints/last.ckpt') #ckpt_path='checkpoints/last.ckpt'
    # trainer.validate(model)
    # model.load_state_dict(torch.load('model.pth', weights_only=True))
    trainer.test(model, test_loader, ckpt_path='checkpoints/last.ckpt')

    # torch.save(model.state_dict(), 'model.pth')