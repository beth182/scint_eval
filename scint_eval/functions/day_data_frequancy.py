import pandas as pd


csv_path = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/data_avail/categorize_days/all_days_for_python.csv'

df = pd.read_csv(csv_path)
df = df.rename(columns={'wd10': 'WD 10', 'wd20': 'WD 20', 'wd30': 'WD 30', 'kdn30': 'Kdown 30', 'kdn40': 'Kdown 40', 'kdn50': 'Kdown 50'})

df[['WD 10', 'WD 20', 'WD 30', 'Kdown 30', 'Kdown 40', 'Kdown 50']].hist(bins=15)


print('end')