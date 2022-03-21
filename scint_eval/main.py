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
                                        obs_path = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/',
                                        # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
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

    # Take only hours with SA made
    # list of hours with SA made
    # CHANGE HERE
    # sa_hours_avail = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    # sa_hours_avail = [1]
    # sa_hours_avail = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 0]
    # sa_hours_avail = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 142
    # sa_hours_avail = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]  # 111

    if DOYstart == 2016111:
        sa_hours_avail = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]  # 111
        in_dir_sa_list = 'C:/Users/beths/Desktop/LANDING/fp_output/111/hourly/'
    elif DOYstart == 2016142:
        sa_hours_avail = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 142
        in_dir_sa_list = 'C:/Users/beths/Desktop/LANDING/fp_output/142/hourly/'
    elif DOYstart == 2016126:
        sa_hours_avail = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]  # 126
        in_dir_sa_list = 'C:/Users/beths/Desktop/LANDING/fp_output/126/hourly/'
    elif DOYstart == 2016123:
        sa_hours_avail = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]  # 123
        in_dir_sa_list = 'C:/Users/beths/Desktop/LANDING/fp_output/123/hourly/'


    else:
        print('DOY NOT A CHOICE')


    time = []
    vals = []
    for hour, val in zip(time_hour, vals_hour):
        if hour.hour in sa_hours_avail:
            time.append(hour)
            vals.append(val)

    # find source area raster
    sa_list = find_source_area.find_source_area(time=time,
                                                in_dir=in_dir_sa_list)

    model_site_dict, percentage_vals_dict, percentage_covered_by_model = grid_percentages.prepare_model_grid_percentages(
        time=time,
        sa_list=sa_list,
        savepath=savepath)



    print('end')



    included_grids, model_site = grid_percentages.determine_which_model_files(model_site_dict, DOYstart_mod,
                                                                              DOYstop_mod, run,
                                                                              instrument,
                                                                              sample, variable,
                                                                              obs_level, model_format, disheight,
                                                                              z0zdlist, saveyn,
                                                                              savepath)

    included_grids = grid_percentages.average_model_grids(included_grids, DOYstart_mod, DOYstop_mod,
                                                          percentage_vals_dict, model_site_dict, model_site)

    # old time series plot
    # centre_and_av = {'Average': included_grids['Average'], 'WAverage': included_grids['WAverage']}
    # times_series.time_series_plot(variable, saveyn, model_site, DOYstart, DOYstop, savepath + 'all_', run, included_grids, group_obs)
    # times_series.time_series_plot(variable, saveyn, model_site, DOYstart, DOYstop, savepath + 'av_', run, centre_and_av, group_obs)

    obs_time, obs_vals = array_retrieval.retrive_arrays_obs(group_obs)
    obs_time, obs_vals = array_retrieval.rm_nans(obs_time, obs_vals)

    # time average the observations
    obs_time_av, obs_vals_av = array_retrieval.time_average_values(obs_vals, obs_time, 10)

    model_grid_vals = {}
    model_grid_time = {}

    for grid_choice in included_grids.keys():
        mod_time, mod_vals = array_retrieval.retrive_arrays_model(included_grids, grid_choice)

        model_grid_vals[grid_choice] = mod_vals
        model_grid_time[grid_choice] = mod_time

    time_eval, obs_vals_eval, mod_vals_eval = array_retrieval.take_common_times(obs_time_av, obs_vals_av,
                                                                                model_grid_time['WAverage'],
                                                                                model_grid_vals['WAverage'])

    plotting_funs.detailed_time_series(obs_time, obs_vals,
                                       model_grid_time, model_grid_vals,
                                       variable, savepath, DOYstart, DOYstop,
                                       model_site_dict,
                                       percentage_covered_by_model)

    return time_eval, obs_vals_eval, mod_vals_eval



    # # PLOT BL STASH CODE
    # file_dict_ukv_13 = file_read.finding_files(model_format,
    #                                            'ukv',
    #                                            DOYstart_mod,
    #                                            DOYstop_mod,
    #                                            'IMU',
    #                                            run,
    #                                            instrument,
    #                                            sample,
    #                                            'BL_H',
    #                                            obs_level,
    #                                            model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
    #                                            )
    #
    # files_ukv_13 = file_read.order_model_stashes('ukv', file_dict_ukv_13, 'BL_H')
    #
    # from scint_eval.functions import stats_of_BL_H
    #
    # stats_of_BL_H.stats_BL_flux(files_ukv_13)
    #
    # ukv_13 = sort_model.sort_models('BL_H', 'ukv', files_ukv_13, disheight, z0zdlist, DOYstart_mod, DOYstop_mod,
    #                                 'IMU', saveyn,
    #                                 savepath, model_format, 'E')
    #
    # BL_H_13_list = [ukv_13[5], ukv_13[6], ukv_13[0], ukv_13[1], ukv_13[10]]
    # included_BL_H = {'BL_H_13': BL_H_13_list}
    # mod_time_13, mod_vals_13 = array_retrieval.retrive_arrays_model(included_BL_H, 'BL_H_13')
    # model_grid_vals['BL_H_13'] = mod_vals_13
    # model_grid_time['BL_H_13'] = mod_time_13
    #
    # plotting_funs.detailed_time_series(obs_time, obs_vals,
    #                                    model_grid_time, model_grid_vals,
    #                                    variable, savepath, DOYstart, DOYstop,
    #                                    model_site_dict,
    #                                    percentage_covered_by_model, BL_H_z=ukv_13[10])

    # 3 arrays to be used for eval:
    # time_eval, obs_vals_eval, mod_vals_eval

    print('END')


########################################################################################################################
# c h o i c e s
# DOYstart_choice = 2016111
# DOYstop_choice = 2016111

# DOYstart_choice = 2016142
# DOYstop_choice = 2016142

DOYstart_choice = 2016126
DOYstop_choice = 2016126

sample = '1min_sa10min'
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

    time_eval, obs_vals_eval, mod_vals_eval = main(obs_site, DOYstart_choice, DOYstop_choice, variable, save_folder, 1, run,
         instrument, sample, model_format, obs_level, scint_path)

    # time_eval_142, obs_vals_eval_142, mod_vals_eval_142 = main(obs_site, DOYstart_choice, DOYstop_choice, variable, save_folder, 1, run,
    #      instrument, sample, model_format, obs_level, scint_path)
    # time_eval_111, obs_vals_eval_111, mod_vals_eval_111 = main(obs_site, 2016111, 2016111, variable,
    #                                                            save_folder, 1, run,
    #                                                            instrument, sample, model_format, obs_level, scint_path)
    #
    # eval_functions.plot_difference(mod_vals_eval_142, obs_vals_eval_142, time_eval_142,
    #                                mod_vals_eval_111, obs_vals_eval_111, time_eval_111,
    #                                save_folder)

print(' ')
print(' ')
print('FINISH')
