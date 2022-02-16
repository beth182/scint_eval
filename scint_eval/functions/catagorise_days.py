# functions for categorizing a day's conditions (to find god case study days, and evaluate alike days)

# imports
import pandas as pd
import numpy as np
import netCDF4 as nc
import datetime as dt
from calendar import isleap
import matplotlib.pyplot as plt

from scint_fp.functions import wx_u_v_components

from scint_eval.functions import roughness
from scint_eval import look_up
from scint_eval.functions import sort_model_wind
from scint_eval.functions import array_retrieval
from scint_eval.functions import file_read


def read_L1_davis_tier_raw(target_DOY, site, average_period, filepath_in):
    """
    Read L1 nc files from the Davis stations (data located on tier raw & processed automatically)
    :return:
    """

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    if filepath_in == "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/" or filepath_in == '/storage/basic/micromet/Tier_raw/data/':
        filedir = filepath_in + DOY_selected.strftime('%Y') + \
                  "/London/L1/" + site + "/DAY/" + DOY_selected.strftime('%j') + "/"

        filename = 'Davis_' + site + '_' + DOY_selected.strftime('%Y') + DOY_selected.strftime('%j') + '_' + str(
            average_period) + 'min.nc'

        filepath = filedir + filename

    nc_file = nc.Dataset(filepath)

    # read wd
    wd_nc = nc_file.variables['dir']
    wd_vals = wd_nc[:, 0, 0, 0]

    ws_nc = nc_file.variables['WS']
    ws_vals = ws_nc[:, 0, 0, 0]

    time_nc = nc_file.variables['time']
    # converts to datetime
    time_dt = nc.num2date(time_nc[:], time_nc.units)

    df_dict = {'time': time_dt, 'wd_L1': wd_vals, 'ws_L1': ws_vals}

    df = pd.DataFrame.from_dict(df_dict)

    df = df.set_index('time')

    return df


def return_L1_to_raw_wd(L1_wd):
    """
    Return the L1 data on tier raw back to "raw" observed wind direction, i.e. remove the automatic processing
    yaw adjustment (which was 305 clockwise from north)
    :param L1_wd:
    :return:
    """

    correction_values = L1_wd - 305
    correction_values[np.where(correction_values < 0)[0]] = correction_values[np.where(correction_values < 0)[0]] + 360

    return correction_values


def correct_obs_wd(wd_df):
    """
    Correct the observed wind direction at BCT
    :param wd_df:
    :return:
    """

    gradient_corr = 1.0127371278374382
    intercept_corr = -26.154468937819814

    # apply adjust
    # y = mx + c  ->  x = (y - c)/m, where x will be BCT adjusted, y will be BCT raw
    bct_adj = (wd_df - intercept_corr) / gradient_corr

    return bct_adj


def determine_predominant_wd(wind_speed, wind_dir):
    """
    Find the average wind direction for a given day
    :return:
    """

    # convert to u and v components
    component_df = wx_u_v_components.ws_wd_to_u_v(wind_speed, wind_dir)

    # take the day's average (only during daytime hours)
    start = dt.time(6, 0, 0)
    end = dt.time(20, 0, 0)
    df_daytime = component_df.between_time(start, end)

    # take the daytime average
    u_mean = df_daytime['u_component'].mean()
    v_mean = df_daytime['v_component'].mean()

    mean_components = pd.DataFrame.from_dict({'u_component': [u_mean], 'v_component': [v_mean]})

    # convert back to a wind speed and direction
    av_daytime_wind = wx_u_v_components.u_v_to_ws_wd(mean_components['u_component'], mean_components['v_component'])

    return av_daytime_wind


def get_model_data_out(DOY_target, files_ukv_wind_in):
    """

    :return:
    """

    # find UKV files for this day

    DOYstart = DOY_target
    DOYstop = DOY_target

    # Finding model files

    # string out of the chosen starting DOY and year
    str_year = str(DOYstart)[:4]
    str_DOY = str(DOYstart)[4:]
    # if the start DOY is the first day of the year:
    if str_DOY == '001':
        # we now have to start with the year before the chosen year
        new_start_year = int(str_year) - 1
        # to get the start DOY, we need to know what the last DOY of the previous year is
        # so is it a leap year (366 days) or not?
        if isleap(new_start_year):
            # leap year
            new_start_DOY = 366
        else:
            # normal year
            new_start_DOY = 365
        # combining the new start year and new DOY start
        DOYstart_mod = int(str(new_start_year) + str(new_start_DOY))
    else:
        new_start_DOY = str(int(str_DOY) - 1).zfill(3)
        DOYstart_mod = int(str_year + new_start_DOY)

    DOYstop_mod = DOYstop - 1

    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['BCT'],
                                                    look_up.obs_zd_macdonald['BCT'])

    if files_ukv_wind_in == "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/" or files_ukv_wind_in == "/storage/basic/micromet/Tier_processing/rv006011/new_data_storage/":

        file_dict_ukv_wind = file_read.finding_files('new',
                                                     'ukv',
                                                     DOYstart_mod,
                                                     DOYstop_mod,
                                                     'IMU',
                                                     '21Z',
                                                     'Davis',
                                                     '1min',
                                                     'wind',
                                                     'L1',
                                                     model_path=files_ukv_wind_in
                                                     )

        files_ukv_wind = file_read.order_model_stashes('ukv', file_dict_ukv_wind, 'wind')

        if files_ukv_wind_in == "/storage/basic/micromet/Tier_processing/rv006011/new_data_storage/":
            savepath = '/storage/basic/micromet/Tier_processing/rv006011/temp/'
        else:
            savepath = 'C:/Users/beths/Desktop/LANDING/'


    else:
        files_ukv_wind = files_ukv_wind_in
        savepath = 'C:/Users/beths/Desktop/LANDING/'

    av_disheight = 145

    ukv_wind = sort_model_wind.sort_models_wind('wind', 'ukv', files_ukv_wind, av_disheight, DOYstart, DOYstop,
                                                'IMU', savepath, 'new', grid_choice='E')

    # define dict for included models
    included_models_ws = {}
    # stringtimelon, stringwindlon, lontimedict, lonwinddict, modheightvaluelon
    group_ukv_ws = [ukv_wind[3], ukv_wind[4], ukv_wind[0], ukv_wind[1], ukv_wind[6]]

    included_models_wd = {}
    # stringtimelon, stringdirlon, lontimedict, londirdict, modheightvaluelon
    group_ukv_wd = [ukv_wind[3], ukv_wind[5], ukv_wind[0], ukv_wind[2], ukv_wind[6]]

    # append to dict
    included_models_ws['ukv'] = group_ukv_ws
    included_models_wd['ukv'] = group_ukv_wd

    mod_time_ws, mod_vals_ws = array_retrieval.retrive_arrays_model(included_models_ws, 'ukv')
    mod_time_wd, mod_vals_wd = array_retrieval.retrive_arrays_model(included_models_wd, 'ukv')

    # level bellow
    # stringtimelon, stringwindlon0, lontimedict, lonwinddict0, modheightvaluelon
    group_ukv_ws0 = [ukv_wind[3], ukv_wind[10], ukv_wind[0], ukv_wind[18], ukv_wind[14]]
    # stringtimelon, stringdirlon0, lontimedict, londirdict0, modheightvaluelon
    group_ukv_wd0 = [ukv_wind[3], ukv_wind[11], ukv_wind[0], ukv_wind[19], ukv_wind[14]]

    # append to dict
    included_models_ws0 = {'ukv': group_ukv_ws0}
    included_models_wd0 = {'ukv': group_ukv_wd0}

    mod_time_ws0, mod_vals_ws0 = array_retrieval.retrive_arrays_model(included_models_ws0, 'ukv')
    mod_time_wd0, mod_vals_wd0 = array_retrieval.retrive_arrays_model(included_models_wd0, 'ukv')

    # level above
    # stringtimelon, stringwindlon2, lontimedict, lonwinddict2, modheightvaluelon
    group_ukv_ws2 = [ukv_wind[3], ukv_wind[12], ukv_wind[0], ukv_wind[20], ukv_wind[15]]
    # stringtimelon, stringdirlon2, lontimedict, londirdict2, modheightvaluelon
    group_ukv_wd2 = [ukv_wind[3], ukv_wind[13], ukv_wind[0], ukv_wind[21], ukv_wind[15]]

    # append to dict
    included_models_ws2 = {'ukv': group_ukv_ws2}
    included_models_wd2 = {'ukv': group_ukv_wd2}

    mod_time_ws2, mod_vals_ws2 = array_retrieval.retrive_arrays_model(included_models_ws2, 'ukv')
    mod_time_wd2, mod_vals_wd2 = array_retrieval.retrive_arrays_model(included_models_wd2, 'ukv')

    ukv_height = ukv_wind[6]
    ukv_height0 = ukv_wind[14]
    ukv_height2 = ukv_wind[15]

    assert mod_time_wd2.all() == mod_time_wd0.all() == mod_time_wd.all()

    return_dict = {'ukv_height': ukv_height, 'ukv_height0': ukv_height0, 'ukv_height2': ukv_height2,
                   'mod_time_wd': mod_time_wd,
                   'mod_vals_wd': mod_vals_wd, 'mod_vals_wd2': mod_vals_wd2, 'mod_vals_wd0': mod_vals_wd0}

    plt.close('all')

    return return_dict


def loop_over_days(DOY_list):
    """

    :param DOY_list:
    :return:
    """

    for DOY in DOY_list:
        print(' ')
        print(DOY)
        print(' ')

        catagorize_one_day(DOY)


def catagorize_one_day(DOY_choice):
    """

    :return:
    """

    # read the observations
    # CHANGE HERE
    # L1_df = read_L1_davis_tier_raw(DOY_choice, 'BCT', 1, 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/Davis_teir_raw_L1/Davis_BCT_2016142_1min.nc')
    # L1_df = read_L1_davis_tier_raw(DOY_choice, 'BCT', 1, 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/Davis_teir_raw_L1/Davis_BCT_2016111_1min.nc')
    # L1_df = read_L1_davis_tier_raw(DOY_choice, 'BCT', 1, "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/")
    L1_df = read_L1_davis_tier_raw(DOY_choice, 'BCT', 1, '/storage/basic/micromet/Tier_raw/data/')

    # change the L1 wind direction back to the raw state (reset & undo the incorrect metadata system yaw adjustment)
    L1_to_raw_wd = return_L1_to_raw_wd(L1_df.wd_L1)

    # correct the wind direction with the new correction
    corrected_wd = correct_obs_wd(L1_to_raw_wd)

    # find the predominant wind direction
    predominant_wind = determine_predominant_wd(L1_df.ws_L1, corrected_wd)

    # CHANGE HERE
    # files_ukv_wind = [{'ukv2016141': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016052021Z_m01s00i002_LON_IMU.nc'},
    #                   {'ukv2016141': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016052021Z_m01s00i003_LON_IMU.nc'}]
    # files_ukv_wind = [{'ukv2016110': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016041921Z_m01s00i002_LON_IMU.nc'},
    #                   {'ukv2016110': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016041921Z_m01s00i003_LON_IMU.nc'}]
    # model_dict = get_model_data_out(DOY_choice, files_ukv_wind)
    # model_dict = get_model_data_out(DOY_choice, "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/")
    model_dict = get_model_data_out(DOY_choice, "/storage/basic/micromet/Tier_processing/rv006011/new_data_storage/")

    hour_ending_obs = corrected_wd[np.where(corrected_wd.index.minute == 0)[0]]

    # combine model output with hour ending obs into a df
    UKV_dict_for_df = {'time': model_dict['mod_time_wd'], 'wd_UKV': model_dict['mod_vals_wd']}
    UKV_df = pd.DataFrame.from_dict(UKV_dict_for_df)
    UKV_df = UKV_df.set_index('time')

    compare_df = pd.concat([UKV_df, hour_ending_obs], axis=1)

    # find the differences between model and hour ending obs
    compare_df['UKV_obs_diff'] = np.abs(compare_df['wd_UKV'] - compare_df['wd_L1'])

    # find the number of hours where this difference is less than 10 degrees
    num_hours_wd_10 = len(np.where(compare_df['UKV_obs_diff'] <= 10)[0])
    num_hours_wd_20 = len(np.where(compare_df['UKV_obs_diff'] <= 20)[0])
    num_hours_wd_30 = len(np.where(compare_df['UKV_obs_diff'] <= 30)[0])

    # create a dataframe with info that I want to retain
    df_return_dict = {'DOY': [DOY_choice], 'predominant_wind': [predominant_wind.wind_direction_convert[0]],
                      'Model_wd_score_10': [num_hours_wd_10], 'Model_wd_score_20': [num_hours_wd_20],
                      'Model_wd_score_30': [num_hours_wd_30]}

    df_return = pd.DataFrame.from_dict(df_return_dict)
    df_return = df_return.set_index('DOY')

    plt.figure(figsize=(14, 10))
    plt.scatter(corrected_wd.index, corrected_wd, marker='.', alpha=0.5, color='grey', label='Corrected Obs')
    plt.plot(model_dict['mod_time_wd'], model_dict['mod_vals_wd'], label='UKV IMU E', color='blue')
    plt.scatter(hour_ending_obs.index, hour_ending_obs, color='green', marker='o', label='hour-ending obs')

    plt.scatter(compare_df['wd_L1'][np.where(compare_df['UKV_obs_diff'] <= 10)[0]].index,
                compare_df['wd_L1'][np.where(compare_df['UKV_obs_diff'] <= 10)[0]],
                s=200, facecolors='none', edgecolors='red', label='w/in 10')

    plt.xlim(min(corrected_wd.index), max(corrected_wd.index))

    # CHANGE HERE
    savefig_path = '/storage/basic/micromet/Tier_processing/rv006011/temp/' + str(DOY_choice) + '.png'
    # savefig_path = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/temp/' + str(DOY_choice) + '.png'
    # savefig_path = 'C:/Users/beths/Desktop/LANDING/' + str(DOY_choice) + '.png'

    plt.savefig(savefig_path)

    # CHANGE HERE
    # csv_filepath = 'C:/Users/beths/Desktop/LANDING/categorize_days.csv'
    csv_filepath = '/storage/basic/micromet/Tier_processing/rv006011/temp/categorize_days.csv'
    # csv_filepath = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/temp/categorize_days.csv'

    # df_return.to_csv(csv_filepath)

    # open existing csv
    existing_csv = pd.read_csv(csv_filepath)
    existing_csv = existing_csv.set_index('DOY')

    combine_df = pd.concat([existing_csv, df_return])
    combine_df = combine_df[~combine_df.index.duplicated(keep='first')]

    combine_df.to_csv(csv_filepath)





# choices
DOY_start = 142
DOY_stop = 142
# DOY_stop = 152

DOY_list_in = []

for i in range(DOY_start, DOY_stop + 1):
    DOY_construct = int('2016' + str(i).zfill(3))
    DOY_list_in.append(DOY_construct)

loop_over_days(DOY_list_in)


