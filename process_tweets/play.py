import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('wvsnowday.csv')
ac = df[df['text'].str.contains(r'All schools.*closed')]
ac['created_at'] = pd.to_datetime(ac['created_at'], infer_datetime_format=True)

ac['date_closed'] = pd.to_datetime(ac['text'].str.extract(r'(\d+/\d+/\d+)'), dayfirst=False).dt.date
ac['district'] = ac['text'].str.extract(r'#(.*)\sCo\s') + ' County School District'

cols_i_want = ['id_str', 'text', 'source', 'favorite_count', 'retweet_count', 'created_at', 'district', 'date_closed']
ac[cols_i_want].to_csv('wv_closures.csv', index=False)

# ac.groupby([ac['date_closed'].dt.year, ac['date_closed'].dt.month]).count().plot(kind='bar')