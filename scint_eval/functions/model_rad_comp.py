# file to look at the components of radiation from the UKV model

# imports
from calendar import isleap
import os
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import DateFormatter

from scint_eval.functions import file_read
from scint_eval.functions import array_retrieval
from scint_eval.functions import sort_model
from scint_eval.functions import observations
from scint_eval import look_up
from scint_eval.functions import roughness

########################################################################################################################
# choices

DOYstart = 2016123
DOYstop = 2016123
model_format = 'new'
scint_path = 12
obs_site = 'IMU'
instrument = 'CNR4'
sample = '15min'
obs_level = 'L1'
run = '21Z'
saveyn = 1

########################################################################################################################

folder_name = str(DOYstart) + '_' + str(DOYstop) + '_' + 'radiation' + '_' + obs_site + '_' + str(scint_path) + '/'
savepath = '../../plots/' + folder_name

if not os.path.exists(savepath):
    os.mkdir(savepath)

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

########################################################################################################################
# OBS
files_obs = file_read.finding_files(model_format, 'obs', DOYstart, DOYstop, 'KSSW', run, instrument, sample,
                                    'kdown', obs_level,
                                    # obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/',
                                    obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                    )

z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                look_up.obs_zd_macdonald[obs_site])

# obs_lup = observations.sort_obs('lup', files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
#                                 savepath, sample,
#                                 instrument)
#
# group_obs_lup = [obs_lup[4], obs_lup[2], obs_lup[3], obs_lup[0], obs_lup[1], obs_lup[5]]
# obs_time_lup, obs_vals_lup = array_retrieval.retrive_arrays_obs(group_obs_lup)
# obs_time_lup, obs_vals_lup = array_retrieval.rm_nans(obs_time_lup, obs_vals_lup)

# obs_kup = observations.sort_obs('kup', files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
#                                 savepath, sample,
#                                 instrument)
#
# group_obs_kup = [obs_kup[6], obs_kup[3], obs_kup[4], obs_kup[0], obs_kup[1], obs_kup[8]]
# obs_time_kup, obs_vals_kup = array_retrieval.retrive_arrays_obs(group_obs_kup)
# obs_time_kup, obs_vals_kup = array_retrieval.rm_nans(obs_time_kup, obs_vals_kup)

obs_kdown = observations.sort_obs('kdown', files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
                                  savepath, sample,
                                  instrument)

group_obs_kdown = [obs_kdown[4], obs_kdown[2], obs_kdown[3], obs_kdown[0], obs_kdown[1], obs_kdown[5]]
obs_time_kdown, obs_vals_kdown = array_retrieval.retrive_arrays_obs(group_obs_kdown)
obs_time_kdown, obs_vals_kdown = array_retrieval.rm_nans(obs_time_kdown, obs_vals_kdown)

obs_ldown = observations.sort_obs('ldown', files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
                                  savepath, sample,
                                  instrument)

group_obs_ldown = [obs_ldown[4], obs_ldown[2], obs_ldown[3], obs_ldown[0], obs_ldown[1], obs_ldown[5]]
obs_time_ldown, obs_vals_ldown = array_retrieval.retrive_arrays_obs(group_obs_ldown)
obs_time_ldown, obs_vals_ldown = array_retrieval.rm_nans(obs_time_ldown, obs_vals_ldown)

# assert obs_time_kdown.all() == obs_time_kup.all()
# kstar = obs_vals_kdown - obs_vals_kup
#
# assert obs_time_ldown.all() == obs_time_lup.all()
# lstar = obs_vals_ldown - obs_vals_lup
#
# assert obs_time_ldown.all() == obs_time_kdown.all()
# qstar = lstar + kstar

print('end')

# ########################################################################################################################
# # lstar
# # file_read.py
# file_dict_ukv_lstar = file_read.finding_files(model_format,
#                                               'ukv',
#                                               DOYstart_mod,
#                                               DOYstop_mod,
#                                               'IMU',
#                                               run,
#                                               instrument,
#                                               sample,
#                                               'lstar',
#                                               obs_level,
#                                               model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
#                                               )
#
# # ordering UKV model files
# # file_read.py
# files_ukv_lstar = file_read.order_model_stashes('ukv', file_dict_ukv_lstar, 'lstar')
#
# ukv_lstar = sort_model.sort_models('lstar', 'ukv', files_ukv_lstar, 0, DOYstart, DOYstop,
#                                    'IMU', savepath, model_format, grid_choice='E')
#
# # define dict for included models
# included_models_lstar = {}
#
# # stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
# group_ukv_lstar = [ukv_lstar[5], ukv_lstar[6], ukv_lstar[0], ukv_lstar[1], ukv_lstar[10]]
# # append to dict
# included_models_lstar['ukv'] = group_ukv_lstar
#
# mod_time_lstar, mod_vals_lstar = array_retrieval.retrive_arrays_model(included_models_lstar, 'ukv')
#
# print('end')
#
# # lstar
# # file_read.py
# file_dict_ukv_lstar_KSSW = file_read.finding_files(model_format,
#                                                    'ukv',
#                                                    DOYstart_mod,
#                                                    DOYstop_mod,
#                                                    'KSSW',
#                                                    run,
#                                                    instrument,
#                                                    sample,
#                                                    'lstar',
#                                                    obs_level,
#                                                    model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
#                                                    )
#
# # ordering UKV model files
# # file_read.py
# files_ukv_lstar_KSSW = file_read.order_model_stashes('ukv', file_dict_ukv_lstar_KSSW, 'lstar')
#
# ukv_lstar_KSSW = sort_model.sort_models('lstar', 'ukv', files_ukv_lstar_KSSW, 0, DOYstart, DOYstop,
#                                         'KSSW', savepath, model_format, grid_choice='E')
#
# # define dict for included models
# included_models_lstar_KSSW = {}
#
# # stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
# group_ukv_lstar_KSSW = [ukv_lstar_KSSW[5], ukv_lstar_KSSW[6], ukv_lstar_KSSW[0], ukv_lstar_KSSW[1], ukv_lstar_KSSW[10]]
# # append to dict
# included_models_lstar_KSSW['ukv'] = group_ukv_lstar_KSSW
#
# mod_time_lstar_KSSW, mod_vals_lstar_KSSW = array_retrieval.retrive_arrays_model(included_models_lstar_KSSW, 'ukv')
#
# print('end')

########################################################################################################################
# ldown

# finding UKV files
# file_read.py
file_dict_ukv_ldown = file_read.finding_files(model_format,
                                              'ukv',
                                              DOYstart_mod,
                                              DOYstop_mod,
                                              'IMU',
                                              run,
                                              instrument,
                                              sample,
                                              'ldown',
                                              obs_level,
                                              model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                              )

# ordering UKV model files
# file_read.py
files_ukv_ldown = file_read.order_model_stashes('ukv', file_dict_ukv_ldown, 'ldown')

ukv_ldown = sort_model.sort_models('ldown', 'ukv', files_ukv_ldown, 0, DOYstart, DOYstop,
                                   'IMU', savepath, model_format, grid_choice='E')

# define dict for included models
included_models_ldown = {}

# stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
group_ukv_ldown = [ukv_ldown[5], ukv_ldown[6], ukv_ldown[0], ukv_ldown[1], ukv_ldown[10]]
# append to dict
included_models_ldown['ukv'] = group_ukv_ldown

mod_time_ldown, mod_vals_ldown = array_retrieval.retrive_arrays_model(included_models_ldown, 'ukv')

print('end')

# finding UKV files
# file_read.py
file_dict_ukv_ldown_KSSW = file_read.finding_files(model_format,
                                                   'ukv',
                                                   DOYstart_mod,
                                                   DOYstop_mod,
                                                   'KSSW',
                                                   run,
                                                   instrument,
                                                   sample,
                                                   'ldown',
                                                   obs_level,
                                                   model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                   )

# ordering UKV model files
# file_read.py
files_ukv_ldown_KSSW = file_read.order_model_stashes('ukv', file_dict_ukv_ldown_KSSW, 'ldown')

ukv_ldown_KSSW = sort_model.sort_models('ldown', 'ukv', files_ukv_ldown_KSSW, 0, DOYstart, DOYstop,
                                        'KSSW', savepath, model_format, grid_choice='E')

# define dict for included models
included_models_ldown_KSSW = {}

# stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
group_ukv_ldown_KSSW = [ukv_ldown_KSSW[5], ukv_ldown_KSSW[6], ukv_ldown_KSSW[0], ukv_ldown_KSSW[1], ukv_ldown_KSSW[10]]
# append to dict
included_models_ldown_KSSW['ukv'] = group_ukv_ldown_KSSW

mod_time_ldown_KSSW, mod_vals_ldown_KSSW = array_retrieval.retrive_arrays_model(included_models_ldown_KSSW, 'ukv')

########################################################################################################################
# kdown

# finding UKV files
# file_read.py
file_dict_ukv_kdown = file_read.finding_files(model_format,
                                              'ukv',
                                              DOYstart_mod,
                                              DOYstop_mod,
                                              'IMU',
                                              run,
                                              instrument,
                                              sample,
                                              'kdown',
                                              obs_level,
                                              model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                              )

# ordering UKV model files
# file_read.py
files_ukv_kdown = file_read.order_model_stashes('ukv', file_dict_ukv_kdown, 'kdown')

ukv_kdown = sort_model.sort_models('kdown', 'ukv', files_ukv_kdown, 0, DOYstart, DOYstop,
                                   'IMU', savepath, model_format, grid_choice='E')

# define dict for included models
included_models_kdown = {}

# stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
group_ukv_kdown = [ukv_kdown[5], ukv_kdown[6], ukv_kdown[0], ukv_kdown[1], ukv_kdown[10]]
# append to dict
included_models_kdown['ukv'] = group_ukv_kdown

mod_time_kdown, mod_vals_kdown = array_retrieval.retrive_arrays_model(included_models_kdown, 'ukv')

# finding UKV files
# file_read.py
file_dict_ukv_kdown_KSSW = file_read.finding_files(model_format,
                                                   'ukv',
                                                   DOYstart_mod,
                                                   DOYstop_mod,
                                                   'KSSW',
                                                   run,
                                                   instrument,
                                                   sample,
                                                   'kdown',
                                                   obs_level,
                                                   model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                   )

# ordering UKV model files
# file_read.py
files_ukv_kdown_KSSW = file_read.order_model_stashes('ukv', file_dict_ukv_kdown_KSSW, 'kdown')

ukv_kdown_KSSW = sort_model.sort_models('kdown', 'ukv', files_ukv_kdown_KSSW, 0, DOYstart, DOYstop,
                                        'KSSW', savepath, model_format, grid_choice='E')

# define dict for included models
included_models_kdown_KSSW = {}

# stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
group_ukv_kdown_KSSW = [ukv_kdown_KSSW[5], ukv_kdown_KSSW[6], ukv_kdown_KSSW[0], ukv_kdown_KSSW[1], ukv_kdown_KSSW[10]]
# append to dict
included_models_kdown_KSSW['ukv'] = group_ukv_kdown_KSSW

mod_time_kdown_KSSW, mod_vals_kdown_KSSW = array_retrieval.retrive_arrays_model(included_models_kdown_KSSW, 'ukv')

########################################################################################################################

# assert mod_time_kdown.all() == mod_time_ldown.all() == mod_time_lstar.all()
# assert mod_time_kdown_KSSW.all() == mod_time_ldown_KSSW.all() == mod_time_lstar_KSSW.all()
# assert mod_time_kdown_KSSW.all() == mod_time_kdown.all()
#
# lup_ukv = mod_vals_lstar - mod_vals_ldown
# lup_ukv_KSSW = mod_vals_lstar_KSSW - mod_vals_ldown_KSSW

plt.close('all')
plt.figure()
plt.scatter(obs_time_kdown, obs_vals_kdown, label='$K_{\downarrow}$', color='red', marker='x')
plt.scatter(obs_time_ldown, obs_vals_ldown, label='$L_{\downarrow}$', color='blue', marker='x')
# plt.scatter(obs_time_kup, obs_vals_kup, label=r'$K_{\uparrow}$', color='green', marker='x')
# plt.scatter(obs_time_lup, -obs_vals_lup, label=r'$L_{\uparrow}$', color='gold', marker='x')
# plt.scatter(obs_time_kdown, kstar, label='K*', color='grey', marker='x')
# plt.scatter(obs_time_ldown, lstar, label='L*', color='paleturquoise', marker='x')
# plt.scatter(obs_time_ldown, qstar, label='Q*', color='black', marker='x')

plt.plot(mod_time_kdown + dt.timedelta(minutes=15), mod_vals_ldown, color='blue', label='UKV IMU')
plt.plot(mod_time_kdown + dt.timedelta(minutes=15), mod_vals_ldown_KSSW, color='blue', linestyle='dotted',
         label='UKV KSSW')
# plt.plot(mod_time_kdown + dt.timedelta(minutes=15), mod_vals_lstar, color='paleturquoise')
# plt.plot(mod_time_kdown + dt.timedelta(minutes=15), mod_vals_lstar_KSSW, color='paleturquoise', linestyle='dotted')
# plt.plot(mod_time_kdown + dt.timedelta(minutes=15), lup_ukv, color='gold')
# plt.plot(mod_time_kdown + dt.timedelta(minutes=15), lup_ukv_KSSW, color='gold', linestyle='dotted')
plt.plot(mod_time_kdown + dt.timedelta(minutes=15), mod_vals_kdown, color='red')
plt.plot(mod_time_kdown + dt.timedelta(minutes=15), mod_vals_kdown_KSSW, color='red', linestyle='dotted')

plt.gca().xaxis.set_major_formatter(DateFormatter('%H'))

plt.xlabel('Time (h)')
plt.ylabel('Flux (W m$^{-2}$)')

plt.legend()
plt.show()

print('end')
