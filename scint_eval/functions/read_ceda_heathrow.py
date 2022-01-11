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
    df_year = df_year.set_index('ob_end_time')

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    # next DOY
    DOY_next = DOY_selected + dt.timedelta(days=1)

    # discard all rows with index time being bigger or equal to 1 in the morning on the next DOY
    DOY_1am = DOY_next + dt.timedelta(hours=1)  # construct 1am datetime for that DOY

    mask = (df_year.index > DOY_selected) & (df_year.index < DOY_1am)

    df_DOY = df_year.loc[mask]

    df = df_DOY[[' mean_wind_dir', ' mean_wind_speed']].copy()

    df = df.rename(columns={' mean_wind_dir': 'WD', ' mean_wind_speed': 'WS'})

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

    df_year = df_year.set_index('Date and Time')

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    # next DOY
    DOY_next = DOY_selected + dt.timedelta(days=1)
    # discard all rows with index time being bigger or equal to 1 in the morning on the next DOY
    DOY_1am = DOY_next + dt.timedelta(hours=1)  # construct 1am datetime for that DOY

    mask = (df_year.index > DOY_selected) & (df_year.index < DOY_1am)

    df_DOY = df_year.loc[mask]

    df = df_DOY[['Hourly Average Direction', 'Hourly Average Speed']].copy()

    df = df.rename(columns={'Hourly Average Direction': 'WD', 'Hourly Average Speed': 'WS'})

    df.WS = pd.to_numeric(df.WS, errors='coerce')
    df.WD = pd.to_numeric(df.WD, errors='coerce')

    # make sure there are no duplicated times
    assert len(df[df.index.duplicated()]) == 0

    return df


def read_BCT_raw(site, target_DOY):
    """

    :return:
    """

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    filedir = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/RAW/" + DOY_selected.strftime('%Y') + \
              "/London/" + site + "/Davis/Daily/" + DOY_selected.strftime('%m') + "/"

    filename = DOY_selected.strftime('%Y') + DOY_selected.strftime('%m') + DOY_selected.strftime(
        '%d') + "_davis_" + site + ".txt"

    filepath = filedir + filename

    # read raw data
    df_raw = pd.read_csv(filepath, header=None, sep=" ")

    # get rid of weird character at start of txt file
    df_raw[0] = df_raw[0].str.replace(r'\x1a', '')

    # replace any empty spaces with nan
    df_raw.replace(r'^\s*$', np.nan, regex=True)

    # add a time col in
    df_raw['time'] = df_raw[0] + ' ' + df_raw[1]
    df_raw['time'] = pd.to_datetime(df_raw['time'])

    # set index
    df_raw.index = df_raw['time']
    df_raw.index = df_raw.index.round('1s')

    # make sure there are no duplicated times
    if len(df_raw[df_raw.index.duplicated()]) != 0:
        dup_ind = np.where(df_raw.index.duplicated() == True)[0]
        for item in dup_ind:
            dup_val = df_raw.index[item]
            where_dup = np.where(df_raw.index == dup_val)[0]
            assert df_raw.iloc[where_dup[1]].all() == df_raw.iloc[where_dup[0]].all()
        drop_rows = df_raw.index[dup_ind]
        df_raw = df_raw.drop(drop_rows)
    assert len(df_raw[df_raw.index.duplicated()]) == 0

    wind_speed = df_raw[6]
    wind_dir = df_raw[7]

    component_df = wx_u_v_components.ws_wd_to_u_v(wind_speed, wind_dir)
    df_raw = pd.concat([df_raw, component_df], axis=1)

    sixty_min = df_raw.resample('60T', closed='right', label='right').mean()

    # get rid of first row where
    if sixty_min.index[0].hour == 0:
        sixty_min = sixty_min[1:]

    av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
    sixty_min = pd.concat([sixty_min, av_comp], axis=1)

    return sixty_min


def read_BCT_used_in_scint(target_DOY):
    """

    :return:
    """

    files_obs = file_read.finding_files('new', 'obs', target_DOY, target_DOY, 'IMU', '21Z', 'LASMkII_Fast', '1min',
                                        'H', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )
    all_days_vars = retrieve_var.retrive_var(files_obs,
                                             ['wind_direction', 'wind_speed', 'wind_speed_adj'])
    all_days_vars = all_days_vars['obs' + str(target_DOY)]
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
    sixty_min = pd.concat([sixty_min, av_comp], axis=1)

    return sixty_min


def read_BCT_L1_tier_raw(targetDOY):
    files_obs = file_read.finding_files('new', 'obs', targetDOY, targetDOY, 'BCT', '21Z', 'Davis', '1min',
                                        'wind', 'L1',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )
    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['BCT'],
                                                    look_up.obs_zd_macdonald['BCT'])
    obs = observations_new_scint.sort_obs_new_scint('wind', files_obs, targetDOY, targetDOY, 'BCT', z0zdlist, 1,
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
    sixty_min = pd.concat([sixty_min, av_comp], axis=1)

    return sixty_min


def hitrate(set1, set2, threshold):
    differences = set2 - set1
    absdiff = abs(differences)

    nlist = []
    for item in absdiff:
        if item <= threshold:
            n = 1.0
        else:
            n = 0.0
        nlist.append(n)
    narray = np.array(nlist)
    # changed to make this a percentage
    hr = narray.mean() * 100
    return hr


# LHR ##############################################################################################################
heath_df_142 = read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
    2016142)
heath_df_111 = read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
    2016111)
heath_df_118 = read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
    2016118)

df_LHR = pd.concat([heath_df_111, heath_df_118, heath_df_142])
df_LHR.index.rename('time', inplace=True)
df_LHR = df_LHR.rename(columns={'WD': 'LHR_WD', 'WS': 'LHR_WS'})

# BCT RAW ##############################################################################################################
BCT_raw_111 = read_BCT_raw('BCT', 2016111)
BCT_raw_118 = read_BCT_raw('BCT', 2016118)
BCT_raw_142 = read_BCT_raw('BCT', 2016142)

df_BCT = pd.concat([BCT_raw_111, BCT_raw_118, BCT_raw_142])
df_BCT.index.rename('time', inplace=True)
df_BCT = df_BCT[['wind_direction_convert', 'wind_speed_convert']]
df_BCT = df_BCT.rename(columns={'wind_direction_convert': 'BCT_WD', 'wind_speed_convert': 'BCT_WS'})

# COMBINE ##############################################################################################################
df = pd.concat([df_LHR, df_BCT], axis=1)

hr_10 = hitrate(df.LHR_WD, df.BCT_WD, 10)
hr_20 = hitrate(df.LHR_WD, df.BCT_WD, 20)

print('end')

# LCY ##############################################################################################################
LC_df_142 = read_NOAA_LCairport(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
    2016142)

LC_df_111 = read_NOAA_LCairport(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
    2016111)

LC_df_118 = read_NOAA_LCairport(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
    2016118)

# SWT ##############################################################################################################
SWT_df_142 = read_SWT_sheet(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
    2016142)

SWT_df_111 = read_SWT_sheet(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
    2016111)

SWT_df_118 = read_SWT_sheet(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
    2016118)

# BCT ADJ ##############################################################################################################
sixty_min_142 = read_BCT_used_in_scint(2016142)
sixty_min_111 = read_BCT_used_in_scint(2016111)
sixty_min_118 = read_BCT_used_in_scint(2016118)

# BCT L1 ##############################################################################################################
sixty_min_bct_raw_142 = read_BCT_L1_tier_raw(2016142)
sixty_min_bct_raw_118 = read_BCT_L1_tier_raw(2016118)
sixty_min_bct_raw_111 = read_BCT_L1_tier_raw(2016111)

# PLOT ##############################################################################################################
plt.figure(figsize=(7, 7))

# add one to one line
one_to_one = [0, 360]
plt.plot(one_to_one, one_to_one, 'k', alpha=0.6)

one_to_one_min = [-20, 340]
# min_line = plt.plot(one_to_one, one_to_one_min, 'b', alpha=0.6)

one_to_one_max = [20, 380]
# max_line = plt.plot(one_to_one, one_to_one_max, 'r', alpha=0.6)
plt.fill_between(one_to_one, one_to_one_min, one_to_one_max, alpha=0.3, color='red')

plt.xlim(0, 360)
plt.ylim(0, 360)

plt.ylabel('dir from other sites (legend)')

# plot option 1 -- LC
plt.xlabel('London City')
plt.scatter(LC_df_142['WD'], heath_df_142['WD'], color='orange', label='Heathrow', marker='o')
plt.scatter(LC_df_111['WD'], heath_df_111['WD'], color='orange', marker='x')
plt.scatter(LC_df_118['WD'], heath_df_118['WD'], color='orange', marker='^')

plt.scatter(LC_df_142['WD'], SWT_df_142['WD'], color='blue', label='SWT', marker='o')
plt.scatter(LC_df_111['WD'], SWT_df_111['WD'], color='blue', marker='x')
plt.scatter(LC_df_118['WD'], SWT_df_118['WD'], color='blue', marker='^')

plt.scatter(LC_df_142['WD'], sixty_min_142['wind_direction_convert'], color='green', label='BCT ADJ', marker='o')
plt.scatter(LC_df_111['WD'], sixty_min_111['wind_direction_convert'], color='green', marker='x')
plt.scatter(LC_df_118['WD'], sixty_min_118['wind_direction_convert'], color='green', marker='^')

plt.scatter(LC_df_142['WD'], sixty_min_bct_raw_142['wind_direction_convert'], color='cyan', label='BCT L1', marker='o')
plt.scatter(LC_df_111['WD'], sixty_min_bct_raw_111['wind_direction_convert'], color='cyan', marker='x')
plt.scatter(LC_df_118['WD'], sixty_min_bct_raw_118['wind_direction_convert'], color='cyan', marker='^')

plt.scatter(LC_df_142['WD'], BCT_raw_142['wind_direction_convert'], color='black', label='BCT RAW', marker='o')
plt.scatter(LC_df_111['WD'], BCT_raw_111['wind_direction_convert'], color='black', marker='x')
plt.scatter(LC_df_118['WD'], BCT_raw_118['wind_direction_convert'], color='black', marker='^')


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
# plt.scatter(heath_df_142['WD'], sixty_min_142['wind_direction_convert'], color='green', label='BCT ADJ', marker='o')
# plt.scatter(heath_df_111['WD'], sixty_min_111['wind_direction_convert'], color='green', marker='x')
# plt.scatter(heath_df_118['WD'], sixty_min_118['wind_direction_convert'], color='green', marker='^')
#
# plt.scatter(heath_df_142['WD'], sixty_min_bct_raw_142['wind_direction_convert'], color='cyan', label='BCT L1', marker='o')
# plt.scatter(heath_df_111['WD'], sixty_min_bct_raw_111['wind_direction_convert'], color='cyan', marker='x')
# plt.scatter(heath_df_118['WD'], sixty_min_bct_raw_118['wind_direction_convert'], color='cyan', marker='^')
#
# plt.scatter(heath_df_142['WD'], BCT_raw_142['wind_direction_convert'], color='black', label='BCT RAW', marker='o')
# plt.scatter(heath_df_111['WD'], BCT_raw_111['wind_direction_convert'], color='black', marker='x')
# plt.scatter(heath_df_118['WD'], BCT_raw_118['wind_direction_convert'], color='black', marker='^')


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
# plt.scatter(SWT_df_142['WD'], sixty_min_142['wind_direction_convert'], color='green', label='BCT ADJ', marker='o')
# plt.scatter(SWT_df_111['WD'], sixty_min_111['wind_direction_convert'], color='green', marker='x')
# plt.scatter(SWT_df_118['WD'], sixty_min_118['wind_direction_convert'], color='green', marker='^')
#
# plt.scatter(SWT_df_142['WD'], sixty_min_bct_raw_142['wind_direction_convert'], color='cyan', label='BCT L1', marker='o')
# plt.scatter(SWT_df_111['WD'], sixty_min_bct_raw_111['wind_direction_convert'], color='cyan', marker='x')
# plt.scatter(SWT_df_118['WD'], sixty_min_bct_raw_118['wind_direction_convert'], color='cyan', marker='^')
#
# plt.scatter(SWT_df_142['WD'], BCT_raw_142['wind_direction_convert'], color='black', label='BCT RAW', marker='o')
# plt.scatter(SWT_df_111['WD'], BCT_raw_111['wind_direction_convert'], color='black', marker='x')
# plt.scatter(SWT_df_118['WD'], BCT_raw_118['wind_direction_convert'], color='black', marker='^')

plt.legend()

plt.savefig('C:/Users/beths/Desktop/LANDING/' + 'wind_scatter.png', bbox_inches='tight')

print('end')
