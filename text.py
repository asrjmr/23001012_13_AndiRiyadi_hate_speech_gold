import re
import pandas as pd

#df1 = pd.read_csv('abusive.csv',encoding='latin-1')
#texts1 = df1.ABUSIVE.tolist()
#print(df1.to_string()) 
#print(texts1)

df = pd.read_csv('data.csv',encoding='latin-1')
texts = df.Tweet.tolist()
#v1 = df.Tweet.head(1)
#texts = v1.tolist()
#v2 = ['cowok','elo']
df1 = pd.read_csv('abusive.csv',encoding='latin-1')
v2=df1.ABUSIVE.tolist()
vTemp=''
for text in texts:  
    for v3 in v2:
        clean_texts = re.sub(v3,'',text)
        text = clean_texts
    vTemp = vTemp + text
#print(texts)
print(vTemp)
