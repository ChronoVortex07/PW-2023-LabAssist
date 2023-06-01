import os
import sys

sys.path.append('pytorchvideo')

import pandas as pd
from sklearn.model_selection import train_test_split

import torch.nn as nn
import torch
from pytorch_lightning import LightningModule, seed_everything, Trainer
from pytorch_lightning.callbacks import ModelCheckpoint, LearningRateMonitor
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.metrics import classification_report
import torchmetrics

seed_everything(0)
torch.set_float32_matmul_precision('medium')

from model import VideoClassifier
from dataloader import video_dataloader

df = pd.read_csv('train.csv')

train_df = pd.read_csv('train.csv')
val_df = pd.read_csv('test.csv')
print(len(train_df), len(val_df))

model = VideoClassifier(
    train_df, 
    val_df, 
    dataloader = video_dataloader,
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
    max_epochs = 15,
    accelerator = 'gpu',
    devices = -1, #-1
    precision = '16-mixed', # 16
    accumulate_grad_batches = 2,
    enable_progress_bar = True,
    num_sanity_val_steps = 0,
    callbacks = [lr_monitor, checkpoint_callback],
)

trainer.fit(model)
# trainer.validate(model)
trainer.test(model)

torch.save(model.state_dict(), 'model.pth')