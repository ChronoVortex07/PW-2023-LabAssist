import os
import sys
sys.path.append('pytorchvideo')

from glob import glob
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from sklearn.model_selection import train_test_split

root_dir = os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)), 'PW-2023-LabAssist')
correct = glob(root_dir+'/dataset/Train/Correct/*.mp4')
incorrect = glob(root_dir+'/dataset/Train/Incorrect/*.mp4')
unmoving = glob(root_dir+'/dataset/Train/Unmoving/*.mp4')
print('correct:', len(correct))
print('incorrect:', len(incorrect))
print('unmoving:', len(unmoving))
labels = [0]*len(correct) + [1]*len(unmoving) + [2]*len(incorrect)
df = pd.DataFrame({'videoPath':correct+unmoving+incorrect, 'trueLabel':labels})
df.to_csv('train.csv', index=False)
print(df.head())