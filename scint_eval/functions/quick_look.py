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
import matplotlib.dates as mdates
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

path_123 = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/123/LASMkII_Fast_IMU_2016123_1min_sa10min.nc'
path_126 = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/126/LASMkII_Fast_IMU_2016126_1min_sa10min.nc'

nc_123 = nc.Dataset(path_123)
nc_126 = nc.Dataset(path_126)

file_time_123 = nc_123.variables['time']
file_time_126 = nc_126.variables['time']

time_dt_123 = nc.num2date(file_time_123[:], file_time_123.units)
time_dt_126 = nc.num2date(file_time_126[:], file_time_126.units)

QH_123 = nc_123.variables['QH'][:]
QH_126 = nc_126.variables['QH'][:]

kdown_123 = nc_123.variables['kdown'][:]
kdown_126 = nc_126.variables['kdown'][:]


nc_df_dict_123 = {'time': time_dt_123, 'QH': QH_123, 'kdown': kdown_123}
nc_df_dict_126 = {'time': time_dt_126, 'QH': QH_126, 'kdown': kdown_126}

nc_df_123 = pd.DataFrame(nc_df_dict_123)
nc_df_126 = pd.DataFrame(nc_df_dict_126)

nc_df_123 = nc_df_123.set_index('time')
nc_df_126 = nc_df_126.set_index('time')

nc_df_123.index = nc_df_123.index.round('1s')
nc_df_126.index = nc_df_126.index.round('1s')

nc_df_123['QH_norm'] = QH_123 / kdown_123
nc_df_126['QH_norm'] = QH_126 / kdown_126

# CHANGE HERE
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/111_10mins.csv'
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/142_10mins.csv'
# csv_111 = 'C:/Users/beths/OneDrive - University of Reading/Working Folder/mask_tests/123_10_mins.csv'

csv_123 = 'C:/Users/beths/Desktop/LANDING/mask_tests/123_10_mins.csv'
csv_126 = 'C:/Users/beths/Desktop/LANDING/mask_tests/126_10_mins.csv'


df_123 = pd.read_csv(csv_123)
df_123.index = df_123['Unnamed: 0']
df_123 = df_123.drop('Unnamed: 0', 1)

df_126 = pd.read_csv(csv_126)
df_126.index = df_126['Unnamed: 0']
df_126 = df_126.drop('Unnamed: 0', 1)

# CHANGE HERE
# df_111.index = pd.to_datetime('2016 111 ' + df_111.index, format='%Y %j %H:%M')
# df_111.index = pd.to_datetime('2016 142 ' + df_111.index, format='%Y %j %H:%M')

df_123.index = pd.to_datetime(df_123.index, format='%d/%m/%Y %H:%M')
df_126.index = pd.to_datetime('2016 126 ' + df_126.index, format='%Y %j %H:%M')

# print('end')


minutes = 10
freq_string = str(minutes) + 'Min'

group_times_123 = df_123.groupby(pd.Grouper(freq=freq_string, label='left')).first()
group_times_126 = df_126.groupby(pd.Grouper(freq=freq_string, label='left')).first()

outputs_df_123 = pd.DataFrame({'Building': [], 'Impervious': [], 'Water': [],'Grass': [],
                                     'Deciduous': [],'Evergreen': [],'Shrub': []})

outputs_df_126 = pd.DataFrame({'Building': [], 'Impervious': [], 'Water': [],'Grass': [],
                                     'Deciduous': [],'Evergreen': [],'Shrub': []})

for i, row in group_times_123.iterrows():
    time = i

    # time_array = np.array([time + dt.timedelta(minutes=i) for i in range(minutes)])
    time_array = np.array([(time + dt.timedelta(minutes=1) - dt.timedelta(minutes=minutes)) + dt.timedelta(minutes=i) for i in range(minutes)])

    Building = df_123['Building'][np.where(df_123.index == time)[0]]
    Impervious = df_123['Impervious'][np.where(df_123.index == time)[0]]
    Water = df_123['Water'][np.where(df_123.index == time)[0]]
    Grass = df_123['Grass'][np.where(df_123.index == time)[0]]
    Deciduous = df_123['Deciduous'][np.where(df_123.index == time)[0]]
    Evergreen = df_123['Evergreen'][np.where(df_123.index == time)[0]]
    Shrub = df_123['Shrub'][np.where(df_123.index == time)[0]]

    df_dict = {'time': time_array}

    lc_types = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

    for lc_type in lc_types:

        lc_type_series = df_123[lc_type][np.where(df_123.index == time)[0]]

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

    outputs_df_123 = outputs_df_123.append(period_df)


for i, row in group_times_126.iterrows():
    time = i

    # time_array = np.array([time + dt.timedelta(minutes=i) for i in range(minutes)])
    time_array = np.array([(time + dt.timedelta(minutes=1) - dt.timedelta(minutes=minutes)) + dt.timedelta(minutes=i) for i in range(minutes)])

    Building = df_126['Building'][np.where(df_126.index == time)[0]]
    Impervious = df_126['Impervious'][np.where(df_126.index == time)[0]]
    Water = df_126['Water'][np.where(df_126.index == time)[0]]
    Grass = df_126['Grass'][np.where(df_126.index == time)[0]]
    Deciduous = df_126['Deciduous'][np.where(df_126.index == time)[0]]
    Evergreen = df_126['Evergreen'][np.where(df_126.index == time)[0]]
    Shrub = df_126['Shrub'][np.where(df_126.index == time)[0]]

    df_dict = {'time': time_array}

    lc_types = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

    for lc_type in lc_types:

        lc_type_series = df_126[lc_type][np.where(df_126.index == time)[0]]

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

    outputs_df_126 = outputs_df_126.append(period_df)


outputs_df_123['sum'] = outputs_df_123.sum(axis=1)
outputs_df_126['sum'] = outputs_df_126.sum(axis=1)

outputs_df_123['Urban'] = outputs_df_123['Building'] + outputs_df_123['Impervious']
outputs_df_126['Urban'] = outputs_df_126['Building'] + outputs_df_126['Impervious']


df_123 = nc_df_123.merge(outputs_df_123, how='inner', left_index=True, right_index=True)
df_126 = nc_df_126.merge(outputs_df_126, how='inner', left_index=True, right_index=True)

df_123 = df_123.dropna()
df_126 = df_126.dropna()


z_123 = np.polyfit(x=df_123.loc[:, 'Urban'], y=df_123.loc[:, 'QH_norm'], deg=1)
z_126 = np.polyfit(x=df_126.loc[:, 'Urban'], y=df_126.loc[:, 'QH_norm'], deg=1)

p_123 = np.poly1d(z_123)
p_126 = np.poly1d(z_126)

df_123['trendline'] = p_123(df_123.loc[:, 'Urban'])
df_126['trendline'] = p_126(df_126.loc[:, 'Urban'])


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


# construct datetime obj for both days with same year day etc. (for colourbar)
format_index_123 = df_123.index.strftime('%H:%M')
format_index_126 = df_126.index.strftime('%H:%M')

index_list_123 = []
for i in format_index_123:
    datetime_object = dt.datetime.strptime(i, '%H:%M')
    index_list_123.append(datetime_object)

index_list_126 = []
for i in format_index_126:
    datetime_object = dt.datetime.strptime(i, '%H:%M')
    index_list_126.append(datetime_object)

df_123.index = index_list_123
df_126.index = index_list_126


df_123_select = df_123[['kdown', 'Urban', 'QH_norm']]
df_123_select.rename({'kdown': 'kdown_123', 'Urban': 'Urban_123', 'QH_norm': 'QH_norm_123'}, axis=1, inplace=True)

df_126_select = df_126[['kdown', 'Urban', 'QH_norm']]
df_126_select.rename({'kdown': 'kdown_126', 'Urban': 'Urban_126', 'QH_norm': 'QH_norm_126'}, axis=1, inplace=True)


combine_df = pd.concat([df_123_select, df_126_select], axis=1)




print('end')


start_dt = dt.datetime(combine_df.index[0].year, combine_df.index[0].month, combine_df.index[0].day, 10)
end_dt = dt.datetime(combine_df.index[0].year, combine_df.index[0].month, combine_df.index[0].day, 14)
where_index = np.where((combine_df.index >= start_dt) & (combine_df.index <= end_dt))[0]


s_123 = ax.scatter(combine_df['Urban_123'][where_index], combine_df['QH_norm_123'][where_index],
                   c=mdates.date2num(combine_df.index)[where_index], marker='x', cmap=cmap, edgecolor='None', label='123')

s_126 = ax.scatter(combine_df['Urban_126'][where_index], combine_df['QH_norm_126'][where_index],
                   c=mdates.date2num(combine_df.index)[where_index], marker='o', cmap=cmap, edgecolor='None', label='126')


plt.legend()

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)

cbar = fig.colorbar(mappable=s_123, cax=cax, orientation="vertical")

cbar.set_ticks(mdates.date2num(combine_df.index[where_index][np.where(combine_df.index[where_index].minute == 0)]))

cbar.ax.set_yticklabels(
    [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
cbar.set_label('Time (h)')

ax.set_xlabel('Built Fraction (%)')
ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')

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





