import pandas as pd
import numpy as np

print('Reading data...')
all_years_snwd = pd.read_csv(filepath_or_buffer='all_years_snwd.csv',
    usecols=[0, 1, 3],
    names=['code','date','depth_mm'],
    dtype={'code': str, 'date': int, 'depth_mm': int})
wv_st_joined = pd.read_csv('wv_stations_joined.csv')
wv_closures = pd.read_csv('wv_closures.csv')
print('Data read.')