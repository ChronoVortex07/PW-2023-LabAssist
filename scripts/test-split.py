import pandas as pd

df = pd.read_csv('train.csv')

random_state = 42

correct = df[df['trueLabel']==0].sample(n=15, random_state=random_state)
unmoving = df[df['trueLabel']==1].sample(n=15, random_state=random_state)
incorrect = df[df['trueLabel']==2].sample(n=15, random_state=random_state)

out_df = pd.concat([correct, unmoving, incorrect])
out_df.to_csv('test.csv', index=False)