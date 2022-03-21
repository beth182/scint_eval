# quick look at nc files

import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import cm
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.dates import DateFormatter
import math

mpl.rcParams.update({'font.size': 15})

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
# path_111 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc'
# path_111 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc'
# path_111 = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/123/LASMkII_Fast_IMU_2016123_1min_sa10min.nc'
# path_111 = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/123/LASMkII_Fast_IMU_2016123_1min_sa10min.nc'
path_111 = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/126/LASMkII_Fast_IMU_2016126_1min_sa10min.nc'

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
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/111_10mins.csv'
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/142_10mins.csv'
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/123_10_mins.csv'

# csv_111 = 'C:/Users/beths/Desktop/LANDING/mask_tests/123_10_mins.csv'
csv_111 = 'C:/Users/beths/Desktop/LANDING/mask_tests/126_10_mins.csv'


df_111 = pd.read_csv(csv_111)
df_111.index = df_111['Unnamed: 0']
df_111 = df_111.drop('Unnamed: 0', 1)

# CHANGE HERE
# df_111.index = pd.to_datetime('2016 111 ' + df_111.index, format='%Y %j %H:%M')
# df_111.index = pd.to_datetime('2016 142 ' + df_111.index, format='%Y %j %H:%M')
# df_111.index = pd.to_datetime(df_111.index, format='%d/%m/%Y %H:%M')
df_111.index = pd.to_datetime('2016 126 ' + df_111.index, format='%Y %j %H:%M')

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

    df_dict = {'time': time_array}

    lc_types = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

    for lc_type in lc_types:

        lc_type_series = df_111[lc_type][np.where(df_111.index == time)[0]]

        if len(lc_type_series) == 0:
            nan_series = pd.Series([np.nan])
            lc_type_series = lc_type_series.append(nan_series)
        else:
            if type(lc_type_series.values[0]) == str:
                lc_type_series.values[0] = 0

        try:
            df_dict[lc_type] = np.ones(len(time_array)) * lc_type_series.values[0]
        except:
            print('end')



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


"""
# QH/Kdn vs Urban fraction, coloured by magnitude of kdown
fig, ax = plt.subplots(figsize=(10,10))

cmap = cm.get_cmap('gist_rainbow') # Colour map (there are many others)

s = ax.scatter(df['Urban'], df['QH_norm'], c=df['kdown'], marker='.', cmap=cmap, edgecolor='None')

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(s, cax=cax)

cax.set_ylabel('$K_{\downarrow}$', rotation=270, labelpad=10)

df.set_index('Urban', inplace=True)
df.trendline.plot(ax=ax, color='k')

ax.set_xlabel('Urban Fraction (%)')
ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')

plt.show()

print('end')
"""

"""
fig, ax = plt.subplots(figsize=(10,10))
cmap = cm.get_cmap('plasma')


# max_urb = math.ceil(max(df['Urban']))
# min_urb = math.floor(min(df['Urban']))

# 126
# max 95
# min 82

# 123
# max 93
# min 81

# manually set to get the same scale for DOY 123 & 126
max_urb = 95
min_urb = 81


# define the bins and normalize
bounds = np.arange(min_urb, max_urb+1, 1)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

s = ax.scatter(df.index, df['QH_norm'], c=df['Urban'], marker='o', cmap=cmap, norm=norm, edgecolor='None')


plt.title('DOY: ' + df.index[0].strftime('%j'))

# plt.scatter(df.index, df['QH_norm'], marker='.')

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(s, cax=cax, cmap=cmap, norm=norm,
    spacing='proportional', ticks=bounds, boundaries=bounds)


plt.gcf().autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))


cax.set_ylabel('Urban Fraction (%)', rotation=270, labelpad=10)




ax.set_xlabel('Time (hh:mm)')
ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')


plt.show()
print('end')
"""




# """

fig, ax = plt.subplots(figsize=(10,10))
cmap = cm.get_cmap('plasma')

start_dt = dt.datetime(df.index[0].year, df.index[0].month, df.index[0].day, 9)
end_dt = dt.datetime(df.index[0].year, df.index[0].month, df.index[0].day, 15)
where_index = np.where((df.index > start_dt) & (df.index < end_dt))[0]


max_kdown = math.ceil(np.nanmax(df['kdown'][where_index]))
min_kdown = math.floor(np.nanmin(df['kdown'][where_index]))

y_axis_max = np.nanmax(df['QH_norm'][where_index])
y_axis_min = np.nanmin(df['QH_norm'][where_index])

x_axis_max = np.nanmax(df['Urban'][where_index])
x_axis_min = np.nanmin(df['Urban'][where_index])

# 126
# max_kdown = 838
# min_kdown = 474
# y_axis_max = 0.8657541561273977
# y_axis_min = 0.044414629306693904
# x_axis_max = 94.78048980236053
# x_axis_min = 82.31962025165558


# 123
# max_kdown = 996
# min_kdown = 150
# y_axis_max = 1.2795449228357636
# y_axis_min = 0.14464143752115785
# x_axis_max = 91.10189974
# x_axis_min = 82.41773844

# for both
max_kdown = 996
min_kdown = 150
y_axis_max = 1.3
y_axis_min = 0
x_axis_max = 94.9
x_axis_min = 82.2

# define the bins and normalize
bounds = np.arange(min_kdown, max_kdown+1, 50)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

s = ax.scatter(df['Urban'][where_index], df['QH_norm'][where_index], c=df['kdown'][where_index], marker='o', cmap=cmap, norm=norm, edgecolor='None')

plt.title('DOY: ' + df.index[0].strftime('%j'))


divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(s, cax=cax, cmap=cmap, norm=norm,
    spacing='proportional', ticks=bounds, boundaries=bounds)

cax.set_ylabel('$K_{\downarrow}$ (W m$^{-2}$)', rotation=270, labelpad=15)



ax.set_xlabel('Built Fraction (%)')
ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')

ax.set_ylim([y_axis_min, y_axis_max])
ax.set_xlim([x_axis_min, x_axis_max])

plt.show()


print('end')
# """



"""
fig = plt.figure(figsize=(10, 8))
ax = plt.subplot(1, 1, 1)

ax.plot(df.index, df['QH'], label='$Q_{H}$', linewidth=1)
ax.plot(df.index, df['kdown'], label='$K_{\downarrow}$', linewidth=1)

ax.set_xlabel('Time (hh:mm)')
ax.set_ylabel('Flux (W $m^{-2}$)')

ax.set_xlim(df.index[0] - dt.timedelta(minutes=10), df.index[-1] + dt.timedelta(minutes=10))

plt.legend()

plt.gcf().autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
plt.title('DOY: ' + df.index[0].strftime('%j'))

plt.show()
"""

print('end')





