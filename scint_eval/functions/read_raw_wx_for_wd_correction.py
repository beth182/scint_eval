# file to read the raw WX data and apply any nessessary correction before averging thse data

# imports
import pandas as pd
from calendar import isleap
import numpy as np

from scint_fp.functions import wx_u_v_components

from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval import look_up
from scint_eval.functions import sort_model_wind
from scint_eval.functions import array_retrieval
from scint_eval.functions import read_ceda_heathrow

import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import DateFormatter


def read_BCT_raw(site, DOY_start, DOY_stop, average_how='1T'):
    """

    :return:
    """

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
        print(DOY)

        DOY_selected = dt.datetime.strptime(str(DOY), '%Y%j')
        filedir = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/RAW/" + DOY_selected.strftime('%Y') + \
                  "/London/" + site + "/Davis/Daily/" + DOY_selected.strftime('%m') + "/"
        filename = DOY_selected.strftime('%Y') + DOY_selected.strftime('%m') + DOY_selected.strftime(
            '%d') + "_davis_" + site + ".txt"
        filepath = filedir + filename
        # filepath = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/20160521_davis_BCT.txt'
        # filepath = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/20160420_davis_BCT.txt'

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

        # correct here
        wd_adj = apply_wd_correction(wind_dir)

        component_df = wx_u_v_components.ws_wd_to_u_v(wind_speed, wd_adj)
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

        # remove any insdtances where DOY is not target DOY (midnight next day etc.)
        averaged_df = averaged_df.drop(
            averaged_df.index[np.where(np.array(averaged_df.index.strftime('%j')) != DOY_selected.strftime('%j'))[0]])

        list_of_DOY_df.append(averaged_df)

    df = pd.concat(list_of_DOY_df)

    return df


def apply_wd_correction(wd,
                        gradient_corr=1.0127371278374382,
                        intercept_corr=-26.154468937819814):
    """

    :param wd:
    :return:
    """

    # apply adjust
    # y = mx + c  ->  x = (y - c)/m, where x will be BCT adjusted, y will be BCT raw
    adj_wd = (wd - intercept_corr) / gradient_corr

    return adj_wd


def get_model_data_out(grid_letter):
    """

    :return:
    """

    ukv_wind = sort_model_wind.sort_models_wind('wind', 'ukv', files_ukv_wind, av_disheight, DOYstart, DOYstop,
                                                'BCT', savepath, model_format, grid_choice=grid_letter)

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

    return return_dict


obs_site = 'BCT'
model_format = 'new'
run = '21Z'
instrument = 'LASMkII_Fast'
sample = '1min'
obs_level = 'L1'
savepath = 'C:/Users/beths/Desktop/LANDING/'

# CHANGE HERE
DOYstart = 2018052
DOYstop = 2018058

# Finding model files
if run == '21Z':
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
else:
    DOYstart_mod = DOYstart
DOYstop_mod = DOYstop - 1

z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                look_up.obs_zd_macdonald[obs_site])

####################################################################################################################
# OBS

DOY_start_year = str(DOYstart)[0:4]
DOY_stop_year = str(DOYstop)[0:4]

# ToDo: handle different years between start and stop
assert DOY_start_year == DOY_stop_year


df_LHR = read_ceda_heathrow.read_ceda_heathrow(
    'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-' +
    DOY_start_year + '01010000-' + DOY_start_year + '12312359_w.csv',
    DOYstart, DOYstop)

df_LHR.index.rename('time', inplace=True)
df_LHR = df_LHR.rename(columns={'WD': 'LHR_WD', 'WS': 'LHR_WS'})

# only have data for LCY for 2016
if int(DOY_start_year) != 2016:
    pass
else:
    LC_df = read_ceda_heathrow.read_NOAA_LCairport(
        'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
        DOYstart, DOYstop)

    LC_df.index.rename('time', inplace=True)
    LC_df = LC_df.rename(columns={'WD': 'WD_LCY', 'WS': 'WS_LCY'})

BCT_raw_df = read_BCT_raw('BCT', DOYstart, DOYstop, average_how='1T')

####################################################################################################################
# MODEL

# CHANGE HERE
# finding UKV files
# file_read.py
file_dict_ukv_wind = file_read.finding_files(model_format,
                                             'ukv',
                                             DOYstart_mod,
                                             DOYstop_mod,
                                             'IMU',
                                             run,
                                             instrument,
                                             sample,
                                             'wind',
                                             obs_level,
                                             model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                             )
# ordering UKV model files
# file_read.py
files_ukv_wind = file_read.order_model_stashes('ukv', file_dict_ukv_wind, 'wind')
# files_ukv_wind = [{'ukv2016141': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016052021Z_m01s00i002_LON_IMU.nc'}, {'ukv2016141': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016052021Z_m01s00i003_LON_IMU.nc'}]
# files_ukv_wind = [
#     {'ukv2016141': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016041921Z_m01s00i002_LON_IMU.nc'},
#     {'ukv2016141': 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/MOUKV_FC2016041921Z_m01s00i003_LON_IMU.nc'}]

av_disheight = 145

# ukv_dictA = get_model_data_out('A')
# ukv_dictB = get_model_data_out('B')
# ukv_dictC = get_model_data_out('C')
# ukv_dictD = get_model_data_out('D')
ukv_dictE = get_model_data_out('E')
# ukv_dictF = get_model_data_out('F')
# ukv_dictG = get_model_data_out('G')
# ukv_dictH = get_model_data_out('H')
# ukv_dictI = get_model_data_out('I')

plt.close('all')

plt.figure()
plt.scatter(BCT_raw_df.index, BCT_raw_df.wind_direction_convert, marker='.', color='grey', label='Obs')

# plt.plot(ukv_dictA['mod_time_wd'], ukv_dictA['mod_vals_wd'], label='UKV A')
# plt.plot(ukv_dictB['mod_time_wd'], ukv_dictB['mod_vals_wd'], label='UKV B')
# plt.plot(ukv_dictC['mod_time_wd'], ukv_dictC['mod_vals_wd'], label='UKV C')
# plt.plot(ukv_dictD['mod_time_wd'], ukv_dictD['mod_vals_wd'], label='UKV D')
plt.plot(ukv_dictE['mod_time_wd'], ukv_dictE['mod_vals_wd'], label='UKV E')
# plt.plot(ukv_dictF['mod_time_wd'], ukv_dictF['mod_vals_wd'], label='UKV F')
# plt.plot(ukv_dictG['mod_time_wd'], ukv_dictG['mod_vals_wd'], label='UKV G')
# plt.plot(ukv_dictH['mod_time_wd'], ukv_dictH['mod_vals_wd'], label='UKV H')
# plt.plot(ukv_dictI['mod_time_wd'], ukv_dictI['mod_vals_wd'], label='UKV I')

if int(DOY_start_year) != 2016:
    pass
else:
    plt.scatter(LC_df.index, LC_df.WD_LCY, label='LCY', color='orange', marker='o')

plt.scatter(df_LHR.index, df_LHR.LHR_WD, label='LHR', color='magenta', marker='o')

plt.gca().xaxis.set_major_formatter(DateFormatter('%j %H'))

plt.legend()
plt.xlabel('time')
plt.ylabel('WD')
plt.show()

print('end')
