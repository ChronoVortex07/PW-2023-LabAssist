import pandas as pd

df = pd.read_csv('dataset/train.csv')

# iterate over each row in the dataframe and edit value of column videoPath
for index, row in df.iterrows():
    subfolder = row['trueLabel']
    df.at[index, 'videoPath'] = 'dataset/Train/'+subfolder+'/'+row['videoPath'].split('/')[-1]
    
print(df)
df.to_csv('train.csv', index=False)

