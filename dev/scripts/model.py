import numpy as np
import os
import torch.nn as nn
import torch
from pytorch_lightning import LightningModule
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.metrics import classification_report
import torchmetrics

class VideoClassifier(LightningModule):
    def __init__(self, learning_rate=1e-3, batch_size=6, num_worker=0):
        super(VideoClassifier, self).__init__()
        # model architecture
        self.video_model = torch.hub.load('facebookresearch/pytorchvideo','efficient_x3d_xs', pretrained=True)
        
        for name, param in self.video_model.named_parameters():
            if 'conv' in name:
                param.requires_grad = False
                
        self.relu = nn.ReLU()
        self.linear = nn.Linear(400, 3)
        self.softmax = nn.Softmax(dim=1)
        
        self.lr = learning_rate
        self.batch_size = batch_size
        self.num_worker = num_worker
        
        # evaluation metrics
        self.metric = torchmetrics.Accuracy(task='multiclass', num_classes=3)
        
        # loss function
        self.criterion = nn.CrossEntropyLoss()
        
        self.labels = torch.tensor([0, 1, 2])
        
        self.train_step_loss = []
        self.train_step_metric = []
        
        self.validation_step_loss = []
        self.validation_step_metric = []
        
        self.test_step_label = []
        self.test_step_pred = []
        
    def forward(self, x):
        x = self.video_model(x)
        x = self.relu(x)
        x = self.linear(x)
        x = self.softmax(x)
        return x
    
    def configure_optimizers(self):
        opt = torch.optim.AdamW(params=self.parameters(), lr=self.lr)
        scheduler = CosineAnnealingLR(opt, T_max=10, eta_min=1e-6, last_epoch=-1)
        return {'optimizer': opt, 'lr_scheduler': scheduler}
    
    def training_step(self, batch, batch_idx):
        video, label = batch['video'], batch['label']
        label = label.flatten().to(torch.int64)
        pred = self(video)
        loss = self.criterion(pred, label)
        metric = self.metric(pred, label.to(torch.int64))
        return {'loss': loss, 'metric': metric.detach()}
    
    def on_training_epoch_end(self, outputs):
        avg_loss = torch.stack([x['loss'] for x in outputs]).mean().cpu().numpy().round(2)
        avg_metric = torch.stack([x['metric'] for x in outputs]).mean().cpu().numpy().round(2)        
        self.log('train_loss', avg_loss, prog_bar=True)
        self.log('train_metric', avg_metric, prog_bar=True)
    
    def validation_step(self, batch, batch_idx):
        video, label = batch['video'], batch['label']
        label = label.flatten().to(torch.int64)
        pred = self(video)
        loss = self.criterion(pred, label)
        metric = self.metric(pred, label.to(torch.int64))
        self.validation_step_loss.append(loss)
        self.validation_step_metric.append(metric)
        return {'val_loss': loss, 'val_metric': metric.detach()}
    
    def on_validation_epoch_end(self):
        avg_loss = torch.stack(self.validation_step_loss).mean().cpu().numpy().round(2)
        avg_metric = torch.stack(self.validation_step_metric).mean().cpu().numpy().round(2)
        
        # if avg_metric more than metric in checkpoints/best/epoch=xx-acc=xx.ckpt, save checkpoint
        # dir = os.listdir('checkpoints/best')
        # if len(dir) > 0:
        #     best_acc = float(dir[0].split('=')[2].split('.')[0])
        #     if avg_metric > best_acc:
        #         os.remove('checkpoints/best/'+dir[0])
        #         self.trainer.save_checkpoint('checkpoints/best/epoch={}-acc={}.ckpt'.format(self.current_epoch, avg_metric))
        # else:
        #     self.trainer.save_checkpoint('checkpoints/best/epoch={}-acc={}.ckpt'.format(self.current_epoch, avg_metric))
        
        self.log('val_loss', avg_loss)
        self.log('val_metric', avg_metric)
    
    def test_step(self, batch, batch_idx):
        video, label = batch['video'], batch['label']
        label = label.flatten().to(torch.int64)
        pred = self(video)
        self.test_step_label.append(label)
        self.test_step_pred.append(pred)
        return {'label': label.detach(), 'pred': pred.detach()}
    
    def on_test_epoch_end(self):
        label = torch.cat(self.test_step_label).cpu().numpy()
        pred = torch.cat(self.test_step_pred).cpu().numpy()
        pred = np.argmax(pred, axis=1)
        print(classification_report(label, pred))
    