from calendar import isleap
import os

from scint_eval import look_up
from scint_eval.functions import file_read
from scint_eval.functions import roughness
from scint_eval.functions import observations
from scint_eval.functions import find_source_area
from scint_eval.functions import grid_percentages
from scint_eval.functions import manipulate_time_objects
from scint_eval.functions import times_series
from scint_eval.functions import plotting_funs
from scint_eval.functions import array_retrieval


def main(obs_site, DOYstart, DOYstop, variable, savepath, saveyn, run, instrument, sample,
         model_format, obs_level, scint_path):
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
                                        obs_path="Z:/micromet/Tier_processing/rv006011/new_data_scint/data/"
                                        )

    # define roughness and displacemet
    # roughness.py
    # note: this step doesn't matter with the scint runs. As we are evaluating a surface model output.
    # This step is only included to keep things running, and values are over-written in the sort_model function.
    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                    look_up.obs_zd_macdonald[obs_site])

    # sort observations
    # observations.py
    obs = observations.sort_obs(variable, files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn, savepath, sample,
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

    # Take only hours with SA made
    # list of hours with SA made
    sa_hours_avail = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    # sa_hours_avail = [5]

    time = []
    vals = []
    for hour, val in zip(time_hour, vals_hour):
        if hour.hour in sa_hours_avail:
            time.append(hour)
            vals.append(val)

    # find source area raster
    sa_list = find_source_area.find_source_area(time=time)

    model_site_dict, percentage_vals_dict = grid_percentages.prepare_model_grid_percentages(time=time,
                                                                                            sa_list=sa_list,
                                                                                            savepath=savepath)

    included_grids, model_site = grid_percentages.determine_which_model_files(model_site_dict, DOYstart_mod,
                                                                              DOYstop_mod, run,
                                                                              instrument,
                                                                              sample, variable,
                                                                              obs_level, model_format, disheight,
                                                                              z0zdlist, saveyn,
                                                                              savepath)

    included_grids = grid_percentages.average_model_grids(included_grids, DOYstart_mod, DOYstop_mod,
                                                          percentage_vals_dict, model_site_dict, model_site)

    # time series plot
    # times_series.time_series_plot(variable, saveyn, model_site, DOYstart, DOYstop, savepath + 'all_', run,
    #                               included_grids, group_obs)
    # times_series.time_series_plot(variable, saveyn, model_site, DOYstart, DOYstop, savepath + 'av_', run, centre_and_av,
    #                               group_obs)

    obs_time, obs_vals = array_retrieval.retrive_arrays_obs(group_obs)
    obs_time, obs_vals = array_retrieval.rm_nans(obs_time, obs_vals)

    mod_time, mod_vals = array_retrieval.retrive_array_model(included_grids, 13)

    obs_time_hourly, obs_vals_hourly, mod_vals = array_retrieval.take_common_times(obs_time, obs_vals, mod_time,
                                                                                   mod_vals)

    model_grid_vals = {}
    model_grid_time = {}

    for grid_choice in included_grids.keys():
        mod_time, mod_vals = array_retrieval.retrive_array_model(included_grids, grid_choice)

        model_grid_vals[grid_choice] = mod_vals
        model_grid_time[grid_choice] = mod_time

    # # wav and av
    # mod_time_av, mod_vals_av = array_retrieval.retrive_array_model(included_grids, 'Average')
    # mod_time_wav, mod_vals_wav = array_retrieval.retrive_array_model(included_grids, 'WAverage')
    #
    # assert mod_time_av.all() == mod_time_wav.all()

    zeff = look_up.scint_zeff[scint_path][0]

    plotting_funs.detailed_time_series(obs_time, obs_vals,
                                       obs_time_hourly, obs_vals_hourly,
                                       model_grid_time, model_grid_vals,
                                       variable, zeff, savepath, DOYstart, DOYstop, model_site_dict)






    print('END')


########################################################################################################################
# c h o i c e s
DOYstart_choice = 2016142
DOYstop_choice = 2016142

sample = '15min'
obs_level = 'L1'
run = '21Z'

# For scintillometry, variable is always sensible heat currently - needn't ever change this
variable = 'H'

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
    save_folder = '../plots/' + folder_name

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    main(obs_site, DOYstart_choice, DOYstop_choice, variable, save_folder, 1, run,
         instrument, sample, model_format, obs_level, scint_path)

print(' ')
print(' ')
print('FINISH')
