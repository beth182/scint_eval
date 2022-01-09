import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

from scint_eval.functions import retrieve_var
from scint_fp.functions import wx_u_v_components
from scint_eval import look_up
from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval.functions import observations_new_scint



def read_ceda_heathrow(filepath, target_DOY):
    """

    :return:
    """

    # read raw data
    df_year = pd.read_csv(filepath)

    # convert times from string to datetime
    df_year['ob_end_time'] = pd.to_datetime(df_year['ob_end_time'], format='%Y-%m-%d %H:%M')

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    df_DOY = df_year.loc[
        (df_year['ob_end_time'].dt.day == DOY_selected.day) & (df_year['ob_end_time'].dt.month == DOY_selected.month)]

    df = df_DOY[['ob_end_time', ' mean_wind_dir', ' mean_wind_speed']].copy()

    df = df.rename(columns={'ob_end_time': 'time', ' mean_wind_dir': 'WD', ' mean_wind_speed': 'WS'})

    df = df.set_index('time')

    df.WS = pd.to_numeric(df.WS, errors='coerce')
    df.WD = pd.to_numeric(df.WD, errors='coerce')

    return df


def read_NOAA_LCairport(filepath, target_DOY):
    """

    :param filepath:
    :param target_DOY:
    :return:
    """

    # read raw data
    df_year = pd.read_csv(filepath)

    # convert times from string to datetime
    df_year['DATE'] = pd.to_datetime(df_year['DATE'], format='%Y-%m-%dT%H:%M:%S')

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    df_DOY = df_year.loc[
        (df_year['DATE'].dt.day == DOY_selected.day) & (df_year['DATE'].dt.month == DOY_selected.month)]

    df = df_DOY[['DATE', 'WND']].copy()

    df['WND'] = df.WND.str.split(',').str[0]

    df['WND'] = df['WND'].astype(int)

    df = df.replace(999, np.nan)

    df = df.rename(columns={'DATE': 'time', 'WND': 'WD'})

    df.WD = pd.to_numeric(df.WD, errors='coerce')

    # LC data is twich an hour, one at 20 mins past, 1 at 50
    # so I am taking the 20 min past data for hourly comparison to other sites
    df = df[(df['time'].dt.minute == 20)]

    df = df.set_index('time')

    return df


def read_SWT_sheet(filepath, target_DOY):
    """

    :return:
    """

    # read raw data
    df_year = pd.read_csv(filepath)

    # convert times from string to datetime
    df_year['Date and Time'] = pd.to_datetime(df_year['Date and Time'], format='%d/%m/%Y %H:%M')

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    df_DOY = df_year.loc[
        (df_year['Date and Time'].dt.day == DOY_selected.day) & (df_year['Date and Time'].dt.month == DOY_selected.month)]

    df = df_DOY[['Date and Time', 'Hourly Average Direction', 'Hourly Average Speed']].copy()

    df = df.rename(columns={'Date and Time': 'time', 'Hourly Average Direction': 'WD', 'Hourly Average Speed': 'WS'})

    df = df.set_index('time')

    df.WS = pd.to_numeric(df.WS, errors='coerce')
    df.WD = pd.to_numeric(df.WD, errors='coerce')

    return df




heath_df_142 = read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
    2016142)

# get LC WD
LC_df_142 = read_NOAA_LCairport(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
    2016142)

SWT_df_142 = read_SWT_sheet('C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
               2016142)

heath_df_111 = read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
    2016111)

# get LC WD
LC_df_111 = read_NOAA_LCairport(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
    2016111)

SWT_df_111 = read_SWT_sheet('C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
               2016111)

heath_df_118 = read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
    2016118)

# get LC WD
LC_df_118 = read_NOAA_LCairport(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
    2016118)

SWT_df_118 = read_SWT_sheet('C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
               2016118)




files_obs = file_read.finding_files('new', 'obs', 2016142, 2016142, 'IMU', '21Z', 'LASMkII_Fast', '1min',
                                        'H', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )
all_days_vars = retrieve_var.retrive_var(files_obs,
                                             ['wind_direction', 'wind_speed', 'wind_speed_adj'])
all_days_vars = all_days_vars['obs' + str(2016142)]
var_dict = all_days_vars
time = var_dict['time']
wind_direction = var_dict['wind_direction']
wind_speed = var_dict['wind_speed_adj']
df_dict = {'time': time, 'wind_direction': wind_direction, 'wind_speed': wind_speed}
df = pd.DataFrame(df_dict)
df = df.set_index('time')
df.index = df.index.round('1s')
component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
df = pd.concat([df, component_df], axis=1)
sixty_min = df.resample('60T', closed='right', label='right').mean()
av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
sixty_min_142 = pd.concat([sixty_min, av_comp], axis=1)



files_obs = file_read.finding_files('new', 'obs', 2016111, 2016111, 'IMU', '21Z', 'LASMkII_Fast', '1min',
                                        'H', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )
all_days_vars = retrieve_var.retrive_var(files_obs,
                                             ['wind_direction', 'wind_speed', 'wind_speed_adj'])
all_days_vars = all_days_vars['obs' + str(2016111)]
var_dict = all_days_vars
time = var_dict['time']
wind_direction = var_dict['wind_direction']
wind_speed = var_dict['wind_speed_adj']
df_dict = {'time': time, 'wind_direction': wind_direction, 'wind_speed': wind_speed}
df = pd.DataFrame(df_dict)
df = df.set_index('time')
df.index = df.index.round('1s')
component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
df = pd.concat([df, component_df], axis=1)
sixty_min = df.resample('60T', closed='right', label='right').mean()
av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
sixty_min_111 = pd.concat([sixty_min, av_comp], axis=1)



files_obs = file_read.finding_files('new', 'obs', 2016118, 2016118, 'IMU', '21Z', 'LASMkII_Fast', '1min',
                                        'H', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )
all_days_vars = retrieve_var.retrive_var(files_obs,
                                             ['wind_direction', 'wind_speed', 'wind_speed_adj'])
all_days_vars = all_days_vars['obs' + str(2016118)]
var_dict = all_days_vars
time = var_dict['time']
wind_direction = var_dict['wind_direction']
wind_speed = var_dict['wind_speed_adj']
df_dict = {'time': time, 'wind_direction': wind_direction, 'wind_speed': wind_speed}
df = pd.DataFrame(df_dict)
df = df.set_index('time')
df.index = df.index.round('1s')
component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
df = pd.concat([df, component_df], axis=1)
sixty_min = df.resample('60T', closed='right', label='right').mean()
av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
sixty_min_118 = pd.concat([sixty_min, av_comp], axis=1)






# BCT RAW
files_obs = file_read.finding_files('new', 'obs', 2016111, 2016111, 'BCT', '21Z', 'Davis', '1min',
                                        'wind', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )
z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['BCT'],
                                                    look_up.obs_zd_macdonald['BCT'])
obs = observations_new_scint.sort_obs_new_scint('wind', files_obs, 2016111, 2016111, 'BCT', z0zdlist, 1,
                                                'C:/Users/beths/Desktop/LANDING/', '15min',
                                                'Davis')
time_key = obs[3][0]
dir_key = obs[5][0]
ws_key = obs[4][0]
time_arr = obs[0][time_key]
dir_arr = obs[2][dir_key]
dir_arr = np.ma.filled(dir_arr, np.nan)
ws_arr = obs[1][ws_key]
ws_arr = np.ma.filled(ws_arr, np.nan)
df_dict = {'time': time_arr, 'wind_direction': dir_arr, 'wind_speed': ws_arr}
df_bct_raw = pd.DataFrame(df_dict)
df_bct_raw = df_bct_raw.set_index('time')
df_bct_raw.index = df_bct_raw.index.round('1s')
component_df = wx_u_v_components.ws_wd_to_u_v(df_bct_raw['wind_speed'], df_bct_raw['wind_direction'])
df_bct_raw = pd.concat([df_bct_raw, component_df], axis=1)
sixty_min = df_bct_raw.resample('60T', closed='right', label='right').mean()
av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
sixty_min_bct_raw_111 = pd.concat([sixty_min, av_comp], axis=1)




files_obs = file_read.finding_files('new', 'obs', 2016142, 2016142, 'BCT', '21Z', 'Davis', '1min',
                                        'wind', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )
z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['BCT'],
                                                    look_up.obs_zd_macdonald['BCT'])
obs = observations_new_scint.sort_obs_new_scint('wind', files_obs, 2016142, 2016142, 'BCT', z0zdlist, 1,
                                                'C:/Users/beths/Desktop/LANDING/', '15min',
                                                'Davis')
time_key = obs[3][0]
dir_key = obs[5][0]
ws_key = obs[4][0]
time_arr = obs[0][time_key]
dir_arr = obs[2][dir_key]
dir_arr = np.ma.filled(dir_arr, np.nan)
ws_arr = obs[1][ws_key]
ws_arr = np.ma.filled(ws_arr, np.nan)
df_dict = {'time': time_arr, 'wind_direction': dir_arr, 'wind_speed': ws_arr}
df_bct_raw = pd.DataFrame(df_dict)
df_bct_raw = df_bct_raw.set_index('time')
df_bct_raw.index = df_bct_raw.index.round('1s')
component_df = wx_u_v_components.ws_wd_to_u_v(df_bct_raw['wind_speed'], df_bct_raw['wind_direction'])
df_bct_raw = pd.concat([df_bct_raw, component_df], axis=1)
sixty_min = df_bct_raw.resample('60T', closed='right', label='right').mean()
av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
sixty_min_bct_raw_142 = pd.concat([sixty_min, av_comp], axis=1)


files_obs = file_read.finding_files('new', 'obs', 2016118, 2016118, 'BCT', '21Z', 'Davis', '1min',
                                        'wind', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )
z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['BCT'],
                                                    look_up.obs_zd_macdonald['BCT'])
obs = observations_new_scint.sort_obs_new_scint('wind', files_obs, 2016118, 2016118, 'BCT', z0zdlist, 1,
                                                'C:/Users/beths/Desktop/LANDING/', '15min',
                                                'Davis')
time_key = obs[3][0]
dir_key = obs[5][0]
ws_key = obs[4][0]
time_arr = obs[0][time_key]
dir_arr = obs[2][dir_key]
dir_arr = np.ma.filled(dir_arr, np.nan)
ws_arr = obs[1][ws_key]
ws_arr = np.ma.filled(ws_arr, np.nan)
df_dict = {'time': time_arr, 'wind_direction': dir_arr, 'wind_speed': ws_arr}
df_bct_raw = pd.DataFrame(df_dict)
df_bct_raw = df_bct_raw.set_index('time')
df_bct_raw.index = df_bct_raw.index.round('1s')
component_df = wx_u_v_components.ws_wd_to_u_v(df_bct_raw['wind_speed'], df_bct_raw['wind_direction'])
df_bct_raw = pd.concat([df_bct_raw, component_df], axis=1)
sixty_min = df_bct_raw.resample('60T', closed='right', label='right').mean()
av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
sixty_min_bct_raw_118 = pd.concat([sixty_min, av_comp], axis=1)




plt.figure(figsize=(7, 7))

# add one to one line
one_to_one = [0, 360]
plt.plot(one_to_one, one_to_one, 'k', alpha=0.6)

plt.ylabel('dir from other sites (legend)')


# plot option 1 -- LC
plt.xlabel('London City')
plt.scatter(LC_df_142['WD'], heath_df_142['WD'], color='orange', label='Heathrow', marker='o')
plt.scatter(LC_df_111['WD'], heath_df_111['WD'], color='orange', marker='x')
plt.scatter(LC_df_118['WD'], heath_df_118['WD'], color='orange', marker='^')

plt.scatter(LC_df_142['WD'], SWT_df_142['WD'], color='blue', label='SWT', marker='o')
plt.scatter(LC_df_111['WD'], SWT_df_111['WD'], color='blue', marker='x')
plt.scatter(LC_df_118['WD'], SWT_df_118['WD'], color='blue', marker='^')

plt.scatter(LC_df_142['WD'], sixty_min_142['wind_direction_convert'], color='green', label='BCT', marker='o')
plt.scatter(LC_df_111['WD'], sixty_min_111['wind_direction_convert'], color='green', marker='x')
plt.scatter(LC_df_118['WD'], sixty_min_118['wind_direction_convert'], color='green', marker='^')

plt.scatter(LC_df_142['WD'], sixty_min_bct_raw_142['wind_direction_convert'], color='cyan', label='BCT RAW', marker='o')
plt.scatter(LC_df_111['WD'], sixty_min_bct_raw_111['wind_direction_convert'], color='cyan', marker='x')
plt.scatter(LC_df_118['WD'], sixty_min_bct_raw_118['wind_direction_convert'], color='cyan', marker='^')


# # plot option 2 -- Heathrow
# plt.xlabel('Heathrow')
# plt.scatter(heath_df_142['WD'], LC_df_142['WD'], color='magenta', label='LC', marker='o')
# plt.scatter(heath_df_111['WD'], LC_df_111['WD'], color='magenta', marker='x')
# plt.scatter(heath_df_118['WD'], LC_df_118['WD'], color='magenta', marker='^')
#
# plt.scatter(heath_df_142['WD'], SWT_df_142['WD'], color='blue', label='SWT', marker='o')
# plt.scatter(heath_df_111['WD'], SWT_df_111['WD'], color='blue', marker='x')
# plt.scatter(heath_df_118['WD'], SWT_df_118['WD'], color='blue', marker='^')
#
# plt.scatter(heath_df_142['WD'], sixty_min_142['wind_direction_convert'], color='green', label='BCT', marker='o')
# plt.scatter(heath_df_111['WD'], sixty_min_111['wind_direction_convert'], color='green', marker='x')
# plt.scatter(heath_df_118['WD'], sixty_min_118['wind_direction_convert'], color='green', marker='^')
#
# plt.scatter(heath_df_142['WD'], sixty_min_bct_raw_142['wind_direction_convert'], color='cyan', label='BCT RAW', marker='o')
# plt.scatter(heath_df_111['WD'], sixty_min_bct_raw_111['wind_direction_convert'], color='cyan', marker='x')
# plt.scatter(heath_df_118['WD'], sixty_min_bct_raw_118['wind_direction_convert'], color='cyan', marker='^')



# # plot option 3 -- SWT
# plt.xlabel('SWT')
# plt.scatter(SWT_df_142['WD'], LC_df_142['WD'], color='magenta', label='LC', marker='o')
# plt.scatter(SWT_df_111['WD'], LC_df_111['WD'], color='magenta', marker='x')
# plt.scatter(SWT_df_118['WD'], LC_df_118['WD'], color='magenta', marker='^')
#
# plt.scatter(SWT_df_142['WD'], heath_df_142['WD'], color='orange', label='Heathrow', marker='o')
# plt.scatter(SWT_df_111['WD'], heath_df_111['WD'], color='orange', marker='x')
# plt.scatter(SWT_df_118['WD'], heath_df_118['WD'], color='orange', marker='^')
#
# plt.scatter(SWT_df_142['WD'], sixty_min_142['wind_direction_convert'], color='green', label='BCT', marker='o')
# plt.scatter(SWT_df_111['WD'], sixty_min_111['wind_direction_convert'], color='green', marker='x')
# plt.scatter(SWT_df_118['WD'], sixty_min_118['wind_direction_convert'], color='green', marker='^')
#
# plt.scatter(SWT_df_142['WD'], sixty_min_bct_raw_142['wind_direction_convert'], color='cyan', label='BCT RAW', marker='o')
# plt.scatter(SWT_df_111['WD'], sixty_min_bct_raw_111['wind_direction_convert'], color='cyan', marker='x')
# plt.scatter(SWT_df_118['WD'], sixty_min_bct_raw_118['wind_direction_convert'], color='cyan', marker='^')





plt.legend()

plt.xlim(0, 360)
plt.ylim(0, 360)

plt.savefig('C:/Users/beths/Desktop/LANDING/' + 'wind_scatter.png', bbox_inches='tight')



print('end')