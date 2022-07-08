from calendar import isleap
import os

from scint_eval import look_up
from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval.functions import observations_new_scint
from scint_eval.functions import observations
from scint_eval.functions import find_source_area
from scint_eval.functions import grid_percentages
from scint_eval.functions import manipulate_time_objects
from scint_eval.functions import times_series
from scint_eval.functions import plotting_funs
from scint_eval.functions import array_retrieval
from scint_eval.functions import sort_model
from scint_eval.functions import eval_functions
from scint_eval.functions import ukv_landuse
from scint_eval.functions import quick_look

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
DOY_start = 2018179
DOY_stop = 2018186


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

files_obs15 = file_read.finding_files('new', 'obs', DOY_start, DOY_stop, 'SWT', '21Z', 'LASMkII_Fast', '15min',
                                      'H', 'L1',
                                      obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                      # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                      )

z0zdlist15 = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['SWT'],
                                                  look_up.obs_zd_macdonald['SWT'])

files_obs12 = file_read.finding_files('new', 'obs', DOY_start, DOY_stop, 'IMU', '21Z', 'LASMkII_Fast', '15min',
                                      'H', 'L1',
                                      obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                      # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                      )

z0zdlist12 = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald['IMU'],
                                                  look_up.obs_zd_macdonald['IMU'])

obs12 = observations.sort_obs('H', files_obs12, DOY_start, DOY_stop, 'IMU', z0zdlist12, 1,
                              'C:/Users/beths/Desktop/LANDING/', '15min',
                              'LASMkII_Fast')

obs15 = observations.sort_obs('H', files_obs15, DOY_start, DOY_stop, 'SWT', z0zdlist15, 1,
                              'C:/Users/beths/Desktop/LANDING/', '15min',
                              'LASMkII_Fast')

group_obs12 = [obs12[4], obs12[2], obs12[3], obs12[0], obs12[1], obs12[5]]
group_obs15 = [obs15[4], obs15[2], obs15[3], obs15[0], obs15[1], obs15[5]]

obs_time12, obs_vals12 = array_retrieval.retrive_arrays_obs(group_obs12)

obs_time15, obs_vals15 = array_retrieval.retrive_arrays_obs(group_obs15)

disheight12 = obs12[6]
disheight15 = obs15[6]

print('END')

# PLOT BL STASH CODE
file_dict_ukv_12 = file_read.finding_files('new',
                                           'ukv',
                                           DOYstart_mod,
                                           DOYstop_mod,
                                           'IMU',
                                           '21Z',
                                           'LASMkII_Fast',
                                           '15min',
                                           'BL_H',
                                           'L1',
                                           model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                           # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                           )

file_dict_ukv_15 = file_read.finding_files('new',
                                           'ukv',
                                           DOYstart_mod,
                                           DOYstop_mod,
                                           'SWT',
                                           '21Z',
                                           'LASMkII_Fast',
                                           '15min',
                                           'BL_H',
                                           'L1',
                                           model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                           # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                           )

files_ukv_12 = file_read.order_model_stashes('ukv', file_dict_ukv_12, 'BL_H')
files_ukv_15 = file_read.order_model_stashes('ukv', file_dict_ukv_15, 'BL_H')

ukv_12 = sort_model.sort_models('BL_H', 'ukv', files_ukv_12, disheight12, DOYstart_mod, DOYstop_mod,
                                'IMU',
                                'C:/Users/beths/Desktop/LANDING/', 'new', 'E')

ukv_15 = sort_model.sort_models('BL_H', 'ukv', files_ukv_15, disheight12, DOYstart_mod, DOYstop_mod,
                                'SWT',
                                'C:/Users/beths/Desktop/LANDING/', 'new', 'E')

BL_H_12_list = [ukv_12[5], ukv_12[6], ukv_12[0], ukv_12[1], ukv_12[10]]
BL_H_15_list = [ukv_15[5], ukv_15[6], ukv_15[0], ukv_15[1], ukv_15[10]]
included_BL_H12 = {'BL_H_12': BL_H_12_list}
included_BL_H15 = {'BL_H_15': BL_H_15_list}
mod_time_12, mod_vals_12 = array_retrieval.retrive_arrays_model(included_BL_H12, 'BL_H_12')
mod_time_15, mod_vals_15 = array_retrieval.retrive_arrays_model(included_BL_H15, 'BL_H_15')

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

plt.figure(figsize=(15, 4))
ax = plt.subplot(1, 1, 1)

plt.scatter(obs_time12, obs_vals12, label='BCT_IMU', marker='.', color='blue')
plt.scatter(obs_time15, obs_vals15, label='SCT_SWT', marker='.', color='red')

plt.plot(mod_time_12, mod_vals_12, label='UKV IMU', color='blue')
plt.plot(mod_time_15, mod_vals_15, label='UKV SWT', color='red')

ax.xaxis.set_major_formatter(DateFormatter('%j'))

# plt.legend()
plt.ylabel('$Q_{H}$ (W m$^{-2}$)')
plt.xlabel('DOY')

import numpy as np

plt.savefig('C:/Users/beths/Desktop/LANDING/save.png', bbox_inches='tight')
# plt.show()

print('END')
