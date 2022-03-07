# file to look at the components of radiation from the UKV model

# imports
from calendar import isleap
import os
import matplotlib.pyplot as plt

from scint_eval.functions import file_read
from scint_eval.functions import array_retrieval
from scint_eval.functions import sort_model

########################################################################################################################
# choices

DOYstart = 2016126
DOYstop = 2016126
model_format = 'new'
scint_path = 12
obs_site = 'IMU'
instrument = 'LASMkII_Fast'
sample = '1min'
obs_level = 'L1'
run = '21Z'

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
# lstar
# file_read.py
file_dict_ukv_lstar = file_read.finding_files(model_format,
                                              'ukv',
                                              DOYstart_mod,
                                              DOYstop_mod,
                                              'IMU',
                                              run,
                                              instrument,
                                              sample,
                                              'lstar',
                                              obs_level,
                                              model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                              )

# ordering UKV model files
# file_read.py
files_ukv_lstar = file_read.order_model_stashes('ukv', file_dict_ukv_lstar, 'lstar')

ukv_lstar = sort_model.sort_models('lstar', 'ukv', files_ukv_lstar, 0, DOYstart, DOYstop,
                                   'IMU', savepath, model_format, grid_choice='E')

# define dict for included models
included_models_lstar = {}

# stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
group_ukv_lstar = [ukv_lstar[5], ukv_lstar[6], ukv_lstar[0], ukv_lstar[1], ukv_lstar[10]]
# append to dict
included_models_lstar['ukv'] = group_ukv_lstar

mod_time_lstar, mod_vals_lstar = array_retrieval.retrive_arrays_model(included_models_lstar, 'ukv')




print('end')



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

########################################################################################################################

assert mod_time_kdown.all() == mod_time_ldown.all() == mod_time_lstar.all()

lup = mod_vals_lstar - mod_vals_ldown


plt.figure()
plt.plot(mod_time_kdown, mod_vals_ldown, label='Ldn')
plt.plot(mod_time_kdown, mod_vals_lstar, label='L*')
plt.plot(mod_time_kdown, lup, label='Lup')
plt.plot(mod_time_kdown, mod_vals_kdown, label='kdn')
plt.legend()
plt.show()


print('end')