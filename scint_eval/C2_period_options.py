from calendar import isleap
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from scint_eval import look_up
from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval.functions import observations
from scint_eval.functions import array_retrieval
from scint_eval.functions import sort_model


def get_path_details(scint_path):
    """

    :return:
    """

    # currently the paths options are
    if scint_path == 12:
        # PATH #12 -- LAS mk11 -- BCT -> IMU -- 0992014 - 3042018
        instrument = 'LASMkII_Fast'
        # defines which site to take the obs from
        # This will always be the site where the receiver is located
        obs_site = 'IMU'
    elif scint_path == 11:
        # PATH #11 -- LAS mk11 -- BTT -> BCT -- 0912014 - 0752016
        instrument = 'LASMkII_Fast'
        obs_site = 'BCT'
    elif scint_path == 13:
        # PATH #13 -- BLS -- IMU -> BTT -- 1802014 - 0752016
        instrument = 'BLS'
        obs_site = 'BTT'
    elif scint_path == 15:
        # PATH #15 -- LAS mk11 -- SCT -> SWT -- 2372017 - CURRENT
        instrument = 'LASMkII_Fast'
        obs_site = 'SWT'

    elif scint_path == 14:
        # PATH #14 -- BLS -- IMU -> SWT -- 0962017 - CURRENT
        instrument = 'BLS'
        obs_site = 'SWT'

    else:
        instrument = None
        obs_site = None
        raise ValueError('Path chosen not an option.')

    return {'instrument': instrument, 'site': obs_site}


def get_model_doy(DOY_start, DOY_stop):
    """

    :return:
    """

    # string out of the chosen starting DOY and year
    str_year = str(DOY_start)[:4]
    str_DOY = str(DOY_start)[4:]
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

    DOYstop_mod = DOY_stop - 1

    return {'DOYstart_mod': DOYstart_mod, 'DOYstop_mod': DOYstop_mod}


# Paths 12 and 15

# # 2017 Autumn 1
# DOY_start = 2017248
# DOY_stop = 2017254

# # 2017 Autumn 2
# DOY_start = 2017258
# DOY_stop = 2017262

# # 2018 spring
# DOY_start = 2018121
# DOY_stop = 2018130

# # 2018 winter
# DOY_start = 2018052
# DOY_stop = 2018058

# # 2018 summer 1
# DOY_start = 2018160
# DOY_stop = 2018172

# 2018 summer 2
# DOY_start = 2018179
# DOY_stop = 2018186



# paths 11, 12, 13

# 2016 summer
# DOY_start = 2016176
# DOY_stop = 2016199
# DOY_start = 2016176
# DOY_stop = 2016183
# DOY_start = 2016184
# DOY_stop = 2016191
# DOY_start = 2016192
# DOY_stop = 2016199

# 2016 Spring
# DOY_start = 2016103
# DOY_stop = 2016108

# DOY_start = 2016134
# DOY_stop = 2016139

# DOY_start = 2016143
# DOY_stop = 2016150


# paths 11, 12

# Autumn 2016
# DOY_start = 2016265
# DOY_stop = 2016270

# DOY_start = 2016273
# DOY_stop = 2016278

# Winter 2017
DOY_start = 2017054
DOY_stop = 2017058


model_doy = get_model_doy(DOY_start, DOY_stop)
DOYstart_mod = model_doy['DOYstart_mod']
DOYstop_mod = model_doy['DOYstop_mod']

path_12_info = get_path_details(12)
path_15_info = get_path_details(15)

las_paths = [11, 12]

path_df = {}

for las_path in las_paths:
    path_info = get_path_details(las_path)

    files_obs = file_read.finding_files('new', 'obs', DOY_start, DOY_stop, path_info['site'], '21Z',
                                        path_info['instrument'], '15min',
                                        'H', 'L1',
                                        # obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )

    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[path_info['site']],
                                                    look_up.obs_zd_macdonald[path_info['site']])

    obs = observations.sort_obs('H', files_obs, DOY_start, DOY_stop, path_info['site'], z0zdlist, 1,
                                'C:/Users/beths/Desktop/LANDING/', '15min',
                                path_info['instrument'])

    group_obs = [obs[4], obs[2], obs[3], obs[0], obs[1], obs[5]]

    obs_time, obs_vals = array_retrieval.retrive_arrays_obs(group_obs)

    df_obs = pd.DataFrame.from_dict({'obs_time': obs_time, 'obs_vals': obs_vals})
    df_obs = df_obs.set_index('obs_time')

    disheight = obs[6]

    file_dict_ukv = file_read.finding_files('new',
                                            'ukv',
                                            DOYstart_mod,
                                            DOYstop_mod,
                                            path_info['site'],
                                            '21Z',
                                            path_info['instrument'],
                                            '15min',
                                            'BL_H',
                                            'L1',
                                            # model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                            model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                            )

    files_ukv = file_read.order_model_stashes('ukv', file_dict_ukv, 'BL_H')

    ukv = sort_model.sort_models('BL_H', 'ukv', files_ukv, disheight, DOYstart_mod, DOYstop_mod,
                                 path_info['site'],
                                 'C:/Users/beths/Desktop/LANDING/', 'new', 'E')

    BL_H_list = [ukv[5], ukv[6], ukv[0], ukv[1], ukv[10]]
    included_BL_H = {'BL_H': BL_H_list}
    mod_time, mod_vals = array_retrieval.retrive_arrays_model(included_BL_H, 'BL_H')

    df_mod = pd.DataFrame.from_dict({'mod_time': mod_time, 'mod_vals': mod_vals})
    df_mod = df_mod.set_index('mod_time')

    path_df[las_path] = {'df_mod': df_mod, 'df_obs': df_obs}


plt.close('all')
plt.figure(figsize=(15, 4))
ax = plt.subplot(1, 1, 1)

for las_path in las_paths:
    print('end')

    ax.scatter(path_df[las_path]['df_obs'].index, path_df[las_path]['df_obs']['obs_vals'], label=str(las_path),
               marker='.')
    ax.plot(path_df[las_path]['df_mod'].index, path_df[las_path]['df_mod']['mod_vals'])

ax.xaxis.set_major_formatter(DateFormatter('%j'))

plt.legend()
ax.set_ylabel('$Q_{H}$ (W m$^{-2}$)')
ax.set_xlabel('DOY')

plt.savefig('C:/Users/beths/Desktop/LANDING/save.png', bbox_inches='tight')

print('END')
