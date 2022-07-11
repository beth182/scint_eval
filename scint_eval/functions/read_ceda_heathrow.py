import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats
import matplotlib.dates as mdates

from scint_eval.functions import retrieve_var
from scint_fp.functions import wx_u_v_components
from scint_eval import look_up
from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval.functions import observations_new_scint


def read_ceda_heathrow(filepath, DOY_start, DOY_stop):
    """

    :return:
    """

    # read raw data
    df_year = pd.read_csv(filepath)

    # convert times from string to datetime
    df_year['ob_end_time'] = pd.to_datetime(df_year['ob_end_time'], format='%Y-%m-%d %H:%M')
    df_year = df_year.set_index('ob_end_time')

    DOY_start_year = str(DOY_start)[0:4]
    DOY_stop_year = str(DOY_stop)[0:4]

    # ToDo: handle different years between start and stop
    assert DOY_start_year == DOY_stop_year

    DOY_start_day = int(str(DOY_start)[4:])
    DOY_stop_day = int(str(DOY_stop)[4:])

    DOY_list = []
    for i in range(DOY_start_day, DOY_stop_day + 1):
        DOY_construct = int(DOY_start_year + str(i).zfill(3))
        DOY_list.append(DOY_construct)

    list_of_DOY_df = []

    for DOY in DOY_list:
        DOY_selected = dt.datetime.strptime(str(DOY), '%Y%j')

        # next DOY
        DOY_next = DOY_selected + dt.timedelta(days=1)

        # discard all rows with index time being bigger or equal to 1 in the morning on the next DOY
        DOY_12am = DOY_next + dt.timedelta(hours=0)

        mask = (df_year.index >= DOY_selected) & (df_year.index < DOY_12am)

        df_DOY = df_year.loc[mask]

        df = df_DOY[[' mean_wind_dir', ' mean_wind_speed']].copy()

        df = df.rename(columns={' mean_wind_dir': 'WD', ' mean_wind_speed': 'WS'})

        df.WS = pd.to_numeric(df.WS, errors='coerce')
        df.WD = pd.to_numeric(df.WD, errors='coerce')

        list_of_DOY_df.append(df)

    df_all = pd.concat(list_of_DOY_df)

    return df_all


def read_NOAA_LCairport(filepath, DOY_start, DOY_stop):
    """

    :param filepath:
    :param target_DOY:
    :return:
    """

    # read raw data
    df_year = pd.read_csv(filepath)

    # convert times from string to datetime
    df_year['DATE'] = pd.to_datetime(df_year['DATE'], format='%Y-%m-%dT%H:%M:%S')

    DOY_start_year = str(DOY_start)[0:4]
    DOY_stop_year = str(DOY_stop)[0:4]

    # ToDo: handle different years between start and stop
    assert DOY_start_year == DOY_stop_year

    DOY_start_day = int(str(DOY_start)[4:])
    DOY_stop_day = int(str(DOY_stop)[4:])

    DOY_list = []
    for i in range(DOY_start_day, DOY_stop_day + 1):
        DOY_construct = int(DOY_start_year + str(i).zfill(3))
        DOY_list.append(DOY_construct)

    list_of_DOY_df = []

    for DOY in DOY_list:

        DOY_selected = dt.datetime.strptime(str(DOY), '%Y%j')

        df_DOY = df_year.loc[
            (df_year['DATE'].dt.day == DOY_selected.day) & (df_year['DATE'].dt.month == DOY_selected.month)]

        df = df_DOY[['DATE', 'WND']].copy()

        wd_val = df.WND.str.split(',').str[0]
        ws_str = df.WND.str.split(',').str[3]

        df['WD'] = df.WND.str.split(',').str[0]
        df['WS'] = df.WND.str.split(',').str[3]

        df['WD'] = df['WD'].astype(int)
        # WIND SPEED IS MULTIPLIED BY 10 IN THIS DATASET. SOURCE OF DOCUMENTATION ON THAT:
        # https://www.visualcrossing.com/resources/documentation/weather-data/how-we-process-integrated-surface-database-historical-weather-data/
        df['WS'] = df['WS'].astype(int) / 10

        df = df.replace(999, np.nan)

        df = df.rename(columns={'DATE': 'time'})

        df.WD = pd.to_numeric(df.WD, errors='coerce')
        df.WS = pd.to_numeric(df.WS, errors='coerce')

        df = df.drop('WND', 1)

        # check if the length of the df is 48?
        if len(df_DOY) != 48:

            times = pd.to_datetime(df['time'])
            start = pd.to_datetime(str(times.min()))
            end = pd.to_datetime(str(times.max()))
            dates = pd.date_range(start=start, end=end, freq='30Min')

            # make sure the missing value isnt at the start or at the end
            # assert len(dates) == 48:

            df = df.set_index('time').reindex(dates)
            # assert len(df) == 48

        else:
            df = df.set_index('time')

        # LC data is twich an hour, one at 20 mins past, 1 at 50
        # so I am taking the 20 min past data for hourly comparison to other sites
        # df = df[(df['time'].dt.minute == 20)]

        # # return the df with hourly index - and separate cols for 20 past and 50 past the hour
        # df_20 = df[(df['time'].dt.minute == 20)]
        # df_50 = df[(df['time'].dt.minute == 50)]
        #
        # df_20 = df_20.set_index('time')
        # df_50 = df_50.set_index('time')
        #
        # df_50.index = df_50.index + dt.timedelta(minutes=10)
        # df_20.index = df_20.index + dt.timedelta(minutes=40)
        #
        # df_50 = df_50.rename(columns={'WD': 'WD_50_mins'})
        # df_20 = df_20.rename(columns={'WD': 'WD_20_mins'})
        #
        # df_combine = pd.concat([df_50, df_20], axis=1)

        list_of_DOY_df.append(df)

    df_all = pd.concat(list_of_DOY_df)

    # return the whole df
    return df_all


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


def read_BCT_raw(site, target_DOY, average_how='LCY'):
    """

    :return:
    """

    print(target_DOY)

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    filedir = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/RAW/" + DOY_selected.strftime('%Y') + \
              "/London/" + site + "/Davis/Daily/" + DOY_selected.strftime('%m') + "/"

    filename = DOY_selected.strftime('%Y') + DOY_selected.strftime('%m') + DOY_selected.strftime(
        '%d') + "_davis_" + site + ".txt"

    filepath = filedir + filename

    # read raw data
    df_raw = pd.read_csv(filepath, header=None, sep=" ", error_bad_lines=False)

    # get rid of weird character at start of txt file
    df_raw[0] = df_raw[0].str.replace(r'\x1a', '')

    # replace any empty spaces with nan
    df_raw.replace(r'^\s*$', np.nan, regex=True)

    # add a time col in
    df_raw['time'] = df_raw[0] + ' ' + df_raw[1]
    df_raw['time'] = pd.to_datetime(df_raw['time'], dayfirst=True)

    # set index
    df_raw.index = df_raw['time']
    df_raw.index = df_raw.index.round('1s')

    # removing all NaT values in index by creating a temp col
    df_raw["TMP"] = df_raw.index.values  # index is a DateTimeIndex
    df_raw = df_raw[df_raw.TMP.notnull()]  # remove all NaT values
    df_raw.drop(["TMP"], axis=1, inplace=True)

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

    if average_how == 'LCY':
        # half hour averages time-ending at 20 past and 50 min past the hour
        averaged_df = df_raw.resample('30T', closed='right', label='right', base=20).mean()
        # get rid of last row where
        if averaged_df.index[-1].hour == 0:
            averaged_df = averaged_df[:-1]

        av_comp = wx_u_v_components.u_v_to_ws_wd(averaged_df['u_component'], averaged_df['v_component'])
        averaged_df = pd.concat([averaged_df, av_comp], axis=1)
    else:

        # other averages averages
        averaged_df = df_raw.resample(average_how, closed='right', label='right').mean()

        if average_how == '60T':
            # get rid of first row where
            if averaged_df.index[0].hour == 0:
                averaged_df = averaged_df[1:]

        av_comp = wx_u_v_components.u_v_to_ws_wd(averaged_df['u_component'], averaged_df['v_component'])
        averaged_df = pd.concat([averaged_df, av_comp], axis=1)

    return averaged_df


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

    # component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
    # df = pd.concat([df, component_df], axis=1)
    # sixty_min = df.resample('60T', closed='right', label='right').mean()
    # av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
    # sixty_min = pd.concat([sixty_min, av_comp], axis=1)
    # return sixty_min

    component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
    df_raw = pd.concat([df, component_df], axis=1)

    # half hour averages time-ending at 20 past and 50 min past the hour
    averaged_df = df_raw.resample('30T', closed='right', label='right', base=20).mean()
    # get rid of last row where
    if averaged_df.index[-1].hour == 0:
        averaged_df = averaged_df[:-1]

    av_comp = wx_u_v_components.u_v_to_ws_wd(averaged_df['u_component'], averaged_df['v_component'])
    averaged_df = pd.concat([averaged_df, av_comp], axis=1)

    return averaged_df


def read_BCT_L1_new_data(targetDOY):
    files_obs = file_read.finding_files('new', 'obs', targetDOY, targetDOY, 'BCT', '21Z', 'Davis', '1min',
                                        'wind', 'L2',
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_scint/data/"
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

    # df_bct_raw['wind_direction'] = df_bct_raw['wind_direction'] + 55
    # df_bct_raw['wind_direction'][np.where(df_bct_raw['wind_direction'] > 360)[0]] = df_bct_raw['wind_direction'] - 360

    # component_df = wx_u_v_components.ws_wd_to_u_v(df_bct_raw['wind_speed'], df_bct_raw['wind_direction'])
    # df_bct_raw = pd.concat([df_bct_raw, component_df], axis=1)
    # sixty_min = df_bct_raw.resample('60T', closed='right', label='right').mean()
    # av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
    # sixty_min = pd.concat([sixty_min, av_comp], axis=1)
    # return sixty_min

    component_df = wx_u_v_components.ws_wd_to_u_v(df_bct_raw['wind_speed'], df_bct_raw['wind_direction'])
    df_raw = pd.concat([df_bct_raw, component_df], axis=1)

    # half hour averages time-ending at 20 past and 50 min past the hour
    averaged_df = df_raw.resample('30T', closed='right', label='right', base=20).mean()
    # get rid of last row where
    if averaged_df.index[-1].hour == 0:
        averaged_df = averaged_df[:-1]

    av_comp = wx_u_v_components.u_v_to_ws_wd(averaged_df['u_component'], averaged_df['v_component'])
    averaged_df = pd.concat([averaged_df, av_comp], axis=1)

    return averaged_df


def read_BCT_L1_tier_raw(targetDOY, averaging_period='60T'):
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

    # df_bct_raw['wind_direction'] = df_bct_raw['wind_direction'] + 55
    # df_bct_raw['wind_direction'][np.where(df_bct_raw['wind_direction'] > 360)[0]] = df_bct_raw['wind_direction'] - 360

    component_df = wx_u_v_components.ws_wd_to_u_v(df_bct_raw['wind_speed'], df_bct_raw['wind_direction'])
    df_bct_raw = pd.concat([df_bct_raw, component_df], axis=1)
    sixty_min = df_bct_raw.resample(averaging_period, closed='right', label='right').mean()
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


def temp_wd_adj(df, wd_col_name):
    """

    :return:
    """

    adj_val = 34.4
    df[wd_col_name] = df[wd_col_name] - adj_val
    df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] = df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] + 360
    df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] = df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] - 360

    # # undo my L1 adjustment
    # my_l1_adj_filtering = 118
    # df[wd_col_name] = df[wd_col_name] - my_l1_adj_filtering
    # df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] = df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] + 360
    # df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] = df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] - 360
    #
    # # undo micromet L1 adjustment: 305 degree yaw --
    # # so, to get from adj to raw, take away 55, or add 305
    # micromet_yaw_adj = 55
    # df[wd_col_name] = df[wd_col_name] + micromet_yaw_adj
    # df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] = df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] + 360
    # df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] = df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] - 360
    #
    # # adding my adjustment for raw to 'correct'
    # # y intercept method
    # adj_val = 29.046
    # df[wd_col_name] = df[wd_col_name] + adj_val
    # df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] = df[wd_col_name][np.where(df[wd_col_name] < 0)[0]] + 360
    # df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] = df[wd_col_name][np.where(df[wd_col_name] > 360)[0]] - 360

    return df


def wdir_diff(wd1, wd2):
    """

    :param wd1:
    :param wd2:
    :return:
    """
    diff1 = (wd1 - wd2) % 360
    diff2 = (wd2 - wd1) % 360
    res = np.minimum(diff1, diff2)
    return res


def mbe(obvs, mod):
    """
    # MEAN BIAS ERROR
    :param obvs:
    :param mod:
    :return:
    """
    differencesmbe = mod - obvs
    mbe_val = differencesmbe.mean()
    return mbe_val


# doy_start = 78
# doy_end = 366

# doy_start = 80
# doy_end = 90


"""
# Reading the pre-made averaged RAW data
# av_raw_bct_dirpath = 'C:/Users/beths/Desktop/LANDING/BCT_RAW_DFS/1min_avs/'
av_raw_bct_dirpath = 'C:/Users/beths/Desktop/LANDING/BCT_RAW_DFS/LCY_avs/'


# find all the files
file_list = []
for i in range(doy_start, doy_end + 1):

    date_int = int('2016' + str(i).zfill(3))

    filepath = av_raw_bct_dirpath + 'bct_raw_LCY_avs_' + str(date_int) + '.csv'
    file_list.append(filepath)

bct_df_list = []

for file in file_list:

    df = pd.read_csv(file)
    # replace any empty spaces with nan
    df = df.replace(r'^\s*$', np.nan, regex=True)

    df['time'] = pd.to_datetime(df['time'], dayfirst=True)

    df = df.set_index('time')

    bct_df_list.append(df)


df_BCT_RAW = pd.concat(bct_df_list)

# remove the period where wind speed and direction are stuck in the raw data
bad_data_start = dt.datetime.strptime('0382016', '%j%Y')
bad_data_end = dt.datetime.strptime('0782016', '%j%Y')
df_BCT_RAW.loc[(df_BCT_RAW.index > bad_data_start) & (df_BCT_RAW.index <= bad_data_end)] = np.nan


print('end')
"""

"""
##############################################################################################################
# Read LHR obs
LHR_df_list = []
for i in range(doy_start, doy_end + 1):
    date_int = int('2016' + str(i))

    heath_df = read_ceda_heathrow(
        'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
        date_int)

    LHR_df_list.append(heath_df)


df_LHR = pd.concat(LHR_df_list)

df_LHR.index.rename('time', inplace=True)
df_LHR = df_LHR.rename(columns={'WD': 'LHR_WD', 'WS': 'LHR_WS'})

print('end')

"""

"""
##############################################################################################################
# Read LCY obs

LCY_df_list = []
for i in range(doy_start, doy_end + 1):
    date_int = int('2016' + str(i))

    LC_df = read_NOAA_LCairport(
        'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
        date_int)


    LCY_df_list.append(LC_df)


df_LCY = pd.concat(LCY_df_list)
df_LCY.index.rename('time', inplace=True)
df_LCY = df_LCY.rename(columns={'WD': 'WD_LCY', 'WS': 'WS_LCY'})

print('end')

"""

"""
# upsample LHR to be the same time resolution as LCY

df_LHR_copy_20 = df_LHR.copy()
df_LHR_copy_50 = df_LHR.copy()

df_LHR_copy_20.index = df_LHR_copy_20.index - dt.timedelta(minutes=40)
df_LHR_copy_50.index = df_LHR_copy_50.index - dt.timedelta(minutes=10)

df_LHR_upsample = pd.concat([df_LHR_copy_20, df_LHR_copy_50])


df_LHR_upsample.sort_index(inplace=True)


# double_LHR = pd.DataFrame(np.repeat(df_LHR.values, 2, axis=0))
# double_LHR.columns = df_LHR.columns
# double_LHR.index = df_LCY.index

df_ap = pd.concat([df_LCY, df_LHR_upsample], axis=1)

"""

"""
# calculating the hit rate


# combine with BCT
df = pd.concat([df_ap, df_BCT_RAW], axis=1)


# remove any low wind speeds from airports
df.loc[df['WS_LCY'] <= 1, ['WD_LCY', 'WS_LCY']] = np.nan
df.loc[df['LHR_WS'] <= 1, ['LHR_WD', 'LHR_WS']] = np.nan
df.loc[df['BCT_RAW_WS'] > 30, ['BCT_RAW_WS']] = np.nan
df.loc[df['BCT_RAW_WS'] < 4, ['BCT_RAW_WS']] = np.nan



df = df.dropna()


df['diff_LHR_LCY'] = np.abs(df['WD_LCY'] - df['LHR_WD'])

BCT_HR_10 = df['BCT_RAW_WD'][np.where(df['diff_LHR_LCY'] <= 10)[0]]
LCY_HR_10 = df['WD_LCY'][np.where(df['diff_LHR_LCY'] <= 10)[0]]

BCT_HR_20 = df['BCT_RAW_WD'][np.where(df['diff_LHR_LCY'] <= 20)[0]]
LCY_HR_20 = df['WD_LCY'][np.where(df['diff_LHR_LCY'] <= 20)[0]]

BCT_HR_0 = df['BCT_RAW_WD'][np.where(df['diff_LHR_LCY'] == 0)[0]]
LCY_HR_0 = df['WD_LCY'][np.where(df['diff_LHR_LCY'] == 0)[0]]
BCT_WS_HR_0 = df['BCT_RAW_WS'][np.where(df['diff_LHR_LCY'] == 0)[0]]

print('end')

"""

"""
# for 2016 after stall (doy 78 onwards) to doy 366
# when BCT is on the y axis and LCY is on the x:
# gradient_corr = 1.0190449892768658
# intercept_corr = -25.858953220432284

gradient_corr = 1.0127371278374382
intercept_corr = -26.154468937819814

# apply adjust
# y = mx + c  ->  x = (y - c)/m, where x will be BCT adjusted, y will be BCT raw
bct_adj = (BCT_HR_0 - intercept_corr) / gradient_corr
"""

"""
# scatter plot

plt.figure(figsize=(7, 7))

# add one to one line
one_to_one = [0, 360]
plt.plot(one_to_one, one_to_one, 'k', alpha=0.6)

# plt.xlim(0, 360)
# plt.ylim(0, 360)

x = LCY_HR_0.copy()
# y = BCT_HR_0.copy()
y = bct_adj

# top left
y[np.where((x < 150) & (y > 250))[0]] = y[np.where((x < 150) & (y > 250))[0]] - 360
# bottom right
y[np.where((x > 250) & (y < 100))[0]] = y[np.where((x > 250) & (y < 100))[0]] + 360

gradient, intercept, r_value, p_value, std_err = stats.linregress(x, y)

mn = np.min(x)
mx = np.max(x)
x1 = np.linspace(mn, mx, 500)
y1 = gradient * x1 + intercept
plt.plot(x1, y1, '-r')

string_for_label = 'm = ' + '%s' % float('%.5g' % gradient) + '\n c = ' + '%s' % float('%.5g' % intercept)

# if the colour bar is a date
# sca = plt.scatter(x, y, label=string_for_label, marker='.', c=mdates.date2num(x.index), cmap=plt.cm.rainbow)
# cbar = plt.colorbar(mappable=sca, orientation="vertical")
# cbar.ax.set_yticklabels(
#         [mdates.num2date(i).strftime('%j') for i in cbar.get_ticks()])  # set ticks of your format
# cbar.set_label('DOY')

cmap = plt.get_cmap('gist_rainbow_r')
sca = plt.scatter(x, y, label=string_for_label, marker='.', c=BCT_WS_HR_0, cmap=cmap, vmin=4, vmax=13)
cmap.set_over('black')
cbar = plt.colorbar(mappable=sca, orientation="vertical", extend='max')
cbar.set_label('WS')


# plt.ylabel('BCT RAW')
plt.ylabel('BCT ADJ')
plt.xlabel('LCY')



# barbican towers
plt.axvspan(251, 260, alpha=0.1, color='red', label='Barbican')
plt.axhspan(251, 260, alpha=0.1, color='red')

# the heron and city point
plt.axvspan(109, 127, alpha=0.1, color='green', label='Heron')
plt.axhspan(109, 127, alpha=0.1, color='green')

# moor house
plt.axvspan(140, 149, alpha=0.1, color='gold', label='Moor')
plt.axhspan(140, 149, alpha=0.1, color='gold')

# London wall buildings
plt.axvspan(178, 194, alpha=0.1, color='saddlebrown', label='LWall')
plt.axhspan(178, 194, alpha=0.1, color='saddlebrown')

# museum of London
plt.axvspan(219, 223, alpha=0.1, color='navy', label='MoL')
plt.axhspan(219, 223, alpha=0.1, color='navy')

# 200 aldersgate st
plt.axvspan(225, 231, alpha=0.1, color='cyan', label='Aldersgate')
plt.axhspan(225, 231, alpha=0.1, color='cyan')

# finsbury tower
plt.axvspan(37, 45, alpha=0.1, color='magenta', label='Finsbury')
plt.axhspan(37, 45, alpha=0.1, color='magenta')

# braithwaite house
plt.axvspan(21, 26, alpha=0.1, color='purple', label='Braithwaite')
plt.axhspan(21, 26, alpha=0.1, color='purple')



# Upper roof
# 343
plt.hlines(y=343, xmin=0, xmax=343, colors='k', linestyles='--', alpha=0.3, label='UL corners')
plt.vlines(x=343, ymin=0, ymax=343, colors='k', linestyles='--', alpha=0.3)
# 25
plt.hlines(y=25, xmin=0, xmax=25, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=25, ymin=0, ymax=25, colors='k', linestyles='--', alpha=0.3)
# 43
plt.hlines(y=43, xmin=0, xmax=43, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=43, ymin=0, ymax=43, colors='k', linestyles='--', alpha=0.3)
# 67
plt.hlines(y=67, xmin=0, xmax=67, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=67, ymin=0, ymax=67, colors='k', linestyles='--', alpha=0.3)
# 83
plt.hlines(y=83, xmin=0, xmax=83, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=83, ymin=0, ymax=83, colors='k', linestyles='--', alpha=0.3)
# 116
plt.hlines(y=116, xmin=0, xmax=116, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=116, ymin=0, ymax=116, colors='k', linestyles='--', alpha=0.3)
# 149
plt.hlines(y=149, xmin=0, xmax=149, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=149, ymin=0, ymax=149, colors='k', linestyles='--', alpha=0.3)
# 168
plt.hlines(y=168, xmin=0, xmax=168, colors='k', linestyles='--', alpha=0.3)
plt.vlines(x=168, ymin=0, ymax=168, colors='k', linestyles='--', alpha=0.3)


# tower corners
# 317
plt.hlines(y=317, xmin=0, xmax=317, colors='red', linestyles='--', alpha=0.3, label='Tower corners')
plt.vlines(x=317, ymin=0, ymax=317, colors='red', linestyles='--', alpha=0.3)
# 79
plt.hlines(y=79, xmin=0, xmax=79, colors='red', linestyles='--', alpha=0.3)
plt.vlines(x=79, ymin=0, ymax=79, colors='red', linestyles='--', alpha=0.3)
# 159
plt.hlines(y=159, xmin=0, xmax=159, colors='red', linestyles='--', alpha=0.3)
plt.vlines(x=159, ymin=0, ymax=159, colors='red', linestyles='--', alpha=0.3)
# 180
plt.hlines(y=180, xmin=0, xmax=180, colors='red', linestyles='--', alpha=0.3)
plt.vlines(x=180, ymin=0, ymax=180, colors='red', linestyles='--', alpha=0.3)


# plt.legend()
plt.legend(loc='center left', bbox_to_anchor=(1.3, 0.5))

plt.savefig('C:/Users/beths/Desktop/LANDING/' + 'TESTadj.png', bbox_inches='tight')
plt.show()

print('end')
"""

"""
##############################################################################################################

# read raw BCT obs from file
BCT_raw_df_list = []

for i in range(doy_start, doy_end + 1):

    date_int = int('2016' + str(i))

    BCT_raw_df = read_BCT_raw('BCT', date_int, average_how='1T')

    BCT_raw_df_list.append(BCT_raw_df)



df_BCT_RAW = pd.concat(BCT_raw_df_list)
df_BCT_RAW.index.rename('time', inplace=True)
df_BCT_RAW = df_BCT_RAW[['wind_direction_convert', 'wind_speed_convert']]
df_BCT_RAW = df_BCT_RAW.rename(columns={'wind_direction_convert': 'BCT_RAW_WD', 'wind_speed_convert': 'BCT_RAW_WS'})

print('end')

"""

"""
# read L1 BCT files
###############################################################################################################

BCT_L1_df_list = []
for i in range(doy_start, doy_end + 1):
    date_int = int('2016' + str(i))

    BCT_L1_df = read_BCT_L1_tier_raw(date_int, averaging_period='1T')

    BCT_L1_df_list.append(BCT_L1_df)

df_BCT_L1 = pd.concat(BCT_L1_df_list)

df_BCT_L1.index.rename('time', inplace=True)
df_BCT_L1 = df_BCT_L1[['wind_direction_convert', 'wind_speed_convert']]
df_BCT_L1 = df_BCT_L1.rename(columns={'wind_direction_convert': 'BCT_L1_WD', 'wind_speed_convert': 'BCT_L1_WS'})

"""

"""
# looking at raw data and L1 data
# combine the dataframes
df_BCT = pd.concat([df_BCT_RAW, df_BCT_L1], axis=1)
# raw minus L1
df_BCT['DIFF_RAW_L1'] = df_BCT['BCT_RAW_WD'] - df_BCT['BCT_L1_WD']
# Adjust L1 back to RAW
df_BCT['LA_ADJ_TO_RAW'] = df_BCT['BCT_L1_WD'] + 55
"""

"""
# Create the averaged raw obs csv files

doy_start = 32
doy_stop = 100

BCT_df_list = []
for i in range(doy_start, doy_stop+1):

    date_int = int('2016'+str(i).zfill(3))

    BCT_raw_df = read_BCT_raw('BCT', date_int, average_how='LCY')

    BCT_raw_df.index.rename('time', inplace=True)
    BCT_raw_df = BCT_raw_df[['wind_direction_convert', 'wind_speed_convert']]
    BCT_raw_df = BCT_raw_df.rename(columns={'wind_direction_convert': 'BCT_RAW_WD', 'wind_speed_convert': 'BCT_RAW_WS'})

    BCT_raw_df.to_csv('C:/Users/beths/Desktop/LANDING/BCT_RAW_DFS/bct_raw_LCY_avs_' + str(date_int) + '.csv')

    BCT_df_list.append(BCT_raw_df)

print('end')

"""

"""
# read BCT used in scint (L2 tier processing)
##############################################################################################################
sixty_min_142 = read_BCT_used_in_scint(2016142)
sixty_min_111 = read_BCT_used_in_scint(2016111)
sixty_min_118 = read_BCT_used_in_scint(2016118)
"""

"""
# read SWT obs
###############################################################################################################
SWT_df_142 = read_SWT_sheet(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
    2016142)

SWT_df_111 = read_SWT_sheet(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
    2016111)

SWT_df_118 = read_SWT_sheet(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
    2016118)

"""

"""
##############################################################################################################
# Read my adjusted L2 obs

BCT_newdata_df_list = []
for i in range(doy_start, doy_end + 1):
    date_int = int('2016' + str(i))

    BCT_newdata_df = read_BCT_L1_new_data(date_int)

    BCT_newdata_df_list.append(BCT_newdata_df)


df_BCT_newdata = pd.concat(BCT_newdata_df_list)


"""

"""
# modular test

modular_test = wdir_diff(LCY_HR_0,BCT_HR_0)

# BCT_HR_0[np.where((LCY_HR_0 < 180) & (BCT_HR_0 > 180))[0]] = BCT_HR_0[np.where((LCY_HR_0 < 180) & (BCT_HR_0 > 180))[0]] - 360
BCT_HR_0[np.where((LCY_HR_0 > 180) & (BCT_HR_0 < 180))[0]] = BCT_HR_0[np.where((LCY_HR_0 > 180) & (BCT_HR_0 < 180))[0]] + 360

mbe_bct_lcy = mbe(LCY_HR_0, BCT_HR_0)

"""
