from calendar import isleap
import os

from scint_eval import look_up
from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval.functions import observations_new_scint
from scint_eval.functions import manipulate_time_objects
from scint_eval.functions import array_retrieval
from scint_eval.functions import plot_profile


def main(obs_site, DOYstart, DOYstop, variable, savepath, saveyn, run, instrument, sample,
         model_format, obs_level):
    """
    MAIN FUNCTION FOR NEW FILE FORMAT MODEL FILES.
    """

    ################################################################################################################
    # if the files are from the 21Z run, then we need to pick files from the DOY before the chosen range
    # this is because we discount the first 3 hours of the files, so we start at midnight the day after the startDOY...
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

    ################################################################################################################
    # finding observation files
    # file_read.py
    files_obs = file_read.finding_files(model_format, 'obs', DOYstart, DOYstop, obs_site, run, instrument, sample,
                                        variable, obs_level,
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )

    # define roughness and displacemet
    # roughness.py
    # note: this step doesn't matter with the scint runs. As we are evaluating a surface model output.
    # This step is only included to keep things running, and values are over-written in the sort_model function.
    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                    look_up.obs_zd_macdonald[obs_site])

    # sort observations
    # observations.py
    obs = observations_new_scint.sort_obs_new_scint(variable, files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
                                                    savepath, sample,
                                                    instrument)

    # grouping obs together
    # [ allobsarenans,  stringtime, stringtemp, obvstimedict,   obvstempdict,   adjustedobvsheight  ]
    group_obs = [obs[4], obs[2], obs[3], obs[0], obs[1], obs[5]]

    # define height of observation - this is different for wind (as there are more outputs from the sort_obs dict)
    if variable == 'wind' or variable == 'kup':
        disheight = obs[8]
    else:
        disheight = obs[6]

    # convert from dictionary to lists
    time_output, vals_output = manipulate_time_objects.dicts_to_lists(time_dict=obs[0],
                                                                      val_dict=obs[1],
                                                                      time_strings=obs[2],
                                                                      val_strings=obs[3])

    # Only take values on the hour
    time_hour, vals_hour = manipulate_time_objects.take_hourly_vars(time=time_output, vals=vals_output)

    obs_time, obs_vals = array_retrieval.retrive_arrays_obs(group_obs)
    obs_time, obs_vals = array_retrieval.rm_nans(obs_time, obs_vals)

    # find model at centre grid (13)
    site_options = look_up.grid_dict[13]

    # FIND BL FLUX
    file_dict_ukv = file_read.finding_files(model_format,
                                            'ukv',
                                            DOYstart_mod,
                                            DOYstop_mod,
                                            site_options[0].split(' ')[0],
                                            run,
                                            instrument,
                                            sample,
                                            variable,
                                            obs_level,
                                            model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                            )
    files_ukv = file_read.order_model_stashes('ukv', file_dict_ukv, variable)

    # FIND SURFACE FLUX
    file_dict_ukv_surf = file_read.finding_files(model_format,
                                                 'ukv',
                                                 DOYstart_mod,
                                                 DOYstop_mod,
                                                 site_options[0].split(' ')[0],
                                                 run,
                                                 instrument,
                                                 sample,
                                                 'H',
                                                 obs_level,
                                                 model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                 )
    files_ukv_surf = file_read.order_model_stashes('ukv', file_dict_ukv_surf, 'H')

    sort_mod = plot_profile.plot_model_profile(variable,
                                               [(k, v) for k, v in files_ukv.items()][0][1],
                                               site_options[0].split(' ')[1],
                                               savepath,
                                               [(k, v) for k, v in files_obs.items()][0][1],
                                               [(k, v) for k, v in files_ukv_surf.items()][0][1])

    print('end')


########################################################################################################################
# c h o i c e s
# CHANGE HERE
DOYstart_choice = 2016142
DOYstop_choice = 2016142

sample = '1min'
obs_level = 'L1'
run = '21Z'

# For scintillometry, variable is always sensible heat currently - needn't ever change this
variable = 'BL_H'

# Description of paths can be seen at
# https://docs.google.com/spreadsheets/d/1gajURSbBKqc0sUAjd-cStRCjUIeh30U2i6GGeRuV-yE/edit#gid=996311903
# all path numbers can re referenced back to here
scint_paths = [12, 14, 15]
scint_path = scint_paths[0]
########################################################################################################################


# currently the paths options are
if scint_path == 12:
    # PATH #12 -- LAS mk11 -- BCT -> IMU -- 0992014 - 3042018
    instrument = 'LASMkII_Fast'
    # defines which site to take the obs from
    # This will always be the site where the receiver is located
    obs_site = 'IMU'

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

file_format = ['old', 'new']
model_format = file_format[1]

if __name__ == "__main__":

    # Join list items using join()
    site_string = obs_site

    folder_name = str(DOYstart_choice) + '_' + str(DOYstop_choice) + '_' + variable + '_' + site_string + '_' + str(
        scint_path) + '/'
    save_folder = '../../plots/' + folder_name

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    main(obs_site, DOYstart_choice, DOYstop_choice, variable, save_folder, 1, run,
         instrument, sample, model_format, obs_level)

print(' ')
print(' ')
print('FINISH')
