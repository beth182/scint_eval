# quick look at nc files

import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.dates import DateFormatter

# looking at the nc files for the days
"""

path_111 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc'
path_142 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc'

# read in files
nc_111 = nc.Dataset(path_111)
nc_142 = nc.Dataset(path_142)

file_time_111 = nc_111.variables['time']
time_dt_111 = nc.num2date(file_time_111[:], file_time_111.units)

file_time_142 = nc_142.variables['time']
time_dt_142 = nc.num2date(file_time_142[:], file_time_142.units)


extent_111 = nc_111.variables['sa_area_km2'][:]
extent_142 = nc_142.variables['sa_area_km2'][:]

# get max vals
max_extent_111 = np.nanmax(extent_111)
max_extent_142 = np.nanmax(extent_142)

min_extent_111 = np.nanmin(extent_111)
min_extent_142 = np.nanmin(extent_142)

max_extent_time_111 = time_dt_111[np.where(extent_111==max_extent_111)[0]]
max_extent_time_142 = time_dt_142[np.where(extent_142==max_extent_142)[0]]

min_extent_time_111 = time_dt_111[np.where(extent_111==min_extent_111)[0]]
min_extent_time_142 = time_dt_142[np.where(extent_142==min_extent_142)[0]]

av_111 = np.nanmean(extent_111)
av_142 = np.nanmean(extent_142)

"""

# Looking at the csv files for fractions for the days
"""

csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/111_10mins.csv'
csv_142 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/142_10mins.csv'

df_111 = pd.read_csv(csv_111)
df_142 = pd.read_csv(csv_142)

max_water_111 = np.nanmax(df_111['Water'])
max_water_time = df_111['Unnamed: 0'][np.where(df_111['Water'] == max_water_111)[0]]

"""


# Looking at a quick plot of normalised QH with land cover fraction for 1 day
# """

# CHANGE HERE
path_111 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc'
# path_111 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc'
nc_111 = nc.Dataset(path_111)

file_time_111 = nc_111.variables['time']
time_dt_111 = nc.num2date(file_time_111[:], file_time_111.units)

QH = nc_111.variables['QH'][:]
kdown = nc_111.variables['kdown'][:]


nc_df_dict = {'time': time_dt_111, 'QH': QH, 'kdown': kdown}

nc_df = pd.DataFrame(nc_df_dict)

nc_df = nc_df.set_index('time')
nc_df.index = nc_df.index.round('1s')


nc_df['QH_norm'] = QH / kdown

# CHANGE HERE
csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/111_10mins.csv'
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/142_10mins.csv'

df_111 = pd.read_csv(csv_111)
df_111.index = df_111['Unnamed: 0']
df_111 = df_111.drop('Unnamed: 0', 1)

# CHANGE HERE
df_111.index = pd.to_datetime('2016 111 ' + df_111.index, format='%Y %j %H:%M')
# df_111.index = pd.to_datetime('2016 142 ' + df_111.index, format='%Y %j %H:%M')

# print('end')


minutes = 10

freq_string = str(minutes) + 'Min'

group_times = df_111.groupby(pd.Grouper(freq=freq_string, label='left')).first()

outputs_df = pd.DataFrame({'Building': [], 'Impervious': [], 'Water': [],'Grass': [],
                                     'Deciduous': [],'Evergreen': [],'Shrub': []})

for i, row in group_times.iterrows():
    time = i

    # time_array = np.array([time + dt.timedelta(minutes=i) for i in range(minutes)])
    time_array = np.array([(time + dt.timedelta(minutes=1) - dt.timedelta(minutes=minutes)) + dt.timedelta(minutes=i) for i in range(minutes)])

    Building = df_111['Building'][np.where(df_111.index == time)[0]]
    Impervious = df_111['Impervious'][np.where(df_111.index == time)[0]]
    Water = df_111['Water'][np.where(df_111.index == time)[0]]
    Grass = df_111['Grass'][np.where(df_111.index == time)[0]]
    Deciduous = df_111['Deciduous'][np.where(df_111.index == time)[0]]
    Evergreen = df_111['Evergreen'][np.where(df_111.index == time)[0]]
    Shrub = df_111['Shrub'][np.where(df_111.index == time)[0]]


    # make pandas df
    df_dict = {'time': time_array,
               'Building': np.ones(len(time_array)) * Building.values[0],
               'Impervious': np.ones(len(time_array)) * Impervious.values[0],
               'Water': np.ones(len(time_array)) * Water.values[0],
               'Grass': np.ones(len(time_array)) * Grass.values[0],
               'Deciduous': np.ones(len(time_array)) * Deciduous.values[0],
               'Evergreen': np.ones(len(time_array)) * Evergreen.values[0],
               'Shrub': np.ones(len(time_array)) * Shrub.values[0]
               }

    period_df = pd.DataFrame(df_dict)
    period_df = period_df.set_index('time')

    outputs_df = outputs_df.append(period_df)

outputs_df['sum'] = outputs_df.sum(axis=1)

outputs_df['Urban'] = outputs_df['Building'] + outputs_df['Impervious']


df = nc_df.merge(outputs_df, how='inner', left_index=True, right_index=True)

df = df.dropna()


z = np.polyfit(x=df.loc[:, 'Urban'], y=df.loc[:, 'QH_norm'], deg=1)
p = np.poly1d(z)
df['trendline'] = p(df.loc[:, 'Urban'])

# fig, ax = plt.subplots(figsize=(10,10))
#
# cmap = cm.get_cmap('gist_rainbow') # Colour map (there are many others)
#
# s = ax.scatter(df['Urban'], df['QH_norm'], c=df['kdown'], marker='.', cmap=cmap, edgecolor='None')
#
# divider = make_axes_locatable(ax)
# cax = divider.append_axes("right", size="5%", pad=0.05)
# plt.colorbar(s, cax=cax)
#
# cax.set_ylabel('$K_{\downarrow}$', rotation=270, labelpad=10)
#
# df.set_index('Urban', inplace=True)
# df.trendline.plot(ax=ax, color='k')
#
# ax.set_xlabel('Urban Fraction (%)')
# ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')


# fig, ax = plt.subplots(figsize=(10,10))
# cmap = cm.get_cmap('plasma') # Colour map (there are many others)
# s = ax.scatter(df.index, df['QH_norm'], c=df['Urban'], marker='.', cmap=cmap, edgecolor='None')
# # plt.scatter(df.index, df['QH_norm'], marker='.')
#
# divider = make_axes_locatable(ax)
# cax = divider.append_axes("right", size="5%", pad=0.05)
# plt.colorbar(s, cax=cax)
#
# plt.gcf().autofmt_xdate()
# ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
#
#
# cax.set_ylabel('Urban Fraction (%)', rotation=270, labelpad=10)
#
#
# ax.set_xlabel('Time (HH:MM)')
# ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')
#
#
# plt.show()



fig = plt.figure(figsize=(10, 8))
ax = plt.subplot(1, 1, 1)

ax.plot(df.index, df['QH'], label='$Q_{H}$', linewidth=1)
ax.plot(df.index, df['kdown'], label='$K_{\downarrow}$', linewidth=1)

ax.set_xlabel('Time (HH:MM)')
ax.set_ylabel('W $m^{-2}$')

ax.set_xlim(df.index[0] - dt.timedelta(minutes=10), df.index[-1] + dt.timedelta(minutes=10))

plt.legend()

plt.gcf().autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

plt.show()


print('end')




# """




