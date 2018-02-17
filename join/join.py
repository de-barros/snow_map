import pandas as pd
import numpy as np
from tqdm import tqdm, tqdm_pandas
tqdm.pandas()

def get_median_depth(closure):
    # Get list of station_ids that match the current closure's district
    station_ids = wv_st_joined[wv_st_joined['district'] == closure['district']]['code'].tolist()
    # Get the date of the current closure and format it to match NOAA
    date_noaa = int(''.join(closure['date_closed'].split('-')))

    depths = []
    for s in station_ids:
        try:
            v = ay.loc[s, date_noaa].values[0]
            depths.append(v)
            print(v)
        except KeyError:
            continue

    print('depths is', depths)
    return np.median(depths)

print('Reading data...')
all_years_snwd = pd.read_csv(filepath_or_buffer='all_years_snwd.csv',
    usecols=[0, 1, 3],
    names=['code','date','depth_mm'],
    dtype={'code': str, 'date': int, 'depth_mm': int})
wv_st_joined = pd.read_csv('wv_stations_joined.csv')
wv_closures = pd.read_csv('wv_closures.csv').dropna()
print('Data read.')


print('Filtering by date...')
results = []
dates = [''.join(x.split('-')) for x in wv_closures['date_closed'].unique().tolist() if str(x) != 'nan']
ay = all_years_snwd[all_years_snwd['date'].isin(dates)].set_index(['code','date'])
print('Filtered by date.')


print('Calculating snowfall medians...')
wv_closures['med_depth'] = wv_closures.progress_apply(get_median_depth, axis=1)
print('\nSnowfall medians calculated.')