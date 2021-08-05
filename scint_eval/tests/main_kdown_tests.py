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
from scint_eval.functions import sort_model
from scint_eval.functions import kdown_timeseries_tests
from scint_eval.functions import kdown_averages_tests


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
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )

    files_obs_par = file_read.finding_files(model_format, 'obs', DOYstart, DOYstop, obs_site, run, 'SKYE', sample,
                                        'PAR_W', obs_level,
                                        obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
                                        )

    # define roughness and displacemet
    # roughness.py
    # note: this step doesn't matter with the scint runs. As we are evaluating a surface model output.
    # This step is only included to keep things running, and values are over-written in the sort_model function.
    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                    look_up.obs_zd_macdonald[obs_site])

    # sort observations
    # observations.py
    obs = observations.sort_obs(variable, files_obs, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
                                                    savepath, sample,
                                                    instrument)

    obs_par = observations.sort_obs('PAR_W', files_obs_par, DOYstart, DOYstop, obs_site, z0zdlist, saveyn,
                                savepath, sample,
                                instrument)

    # grouping obs together
    # [ allobsarenans,  stringtime, stringtemp, obvstimedict,   obvstempdict,   adjustedobvsheight  ]
    group_obs = [obs[4], obs[2], obs[3], obs[0], obs[1], obs[5]]

    group_obs_par = [obs_par[4], obs_par[2], obs_par[3], obs_par[0], obs_par[1], obs_par[5]]

    # define height of observation - this is different for wind (as there are more outputs from the sort_obs dict)
    if variable == 'wind' or variable == 'kup':
        disheight = obs[8]
    else:
        disheight = obs[6]

    # finding UKV files
    # file_read.py
    file_dict_ukv = file_read.finding_files(model_format,
                                            'ukv',
                                            DOYstart_mod,
                                            DOYstop_mod,
                                            obs_site,
                                            run,
                                            instrument,
                                            sample,
                                            variable,
                                            obs_level,
                                            model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                            )

    # ordering UKV model files
    # file_read.py
    files_ukv = file_read.order_model_stashes('ukv', file_dict_ukv, variable)

    # models.py

    ukv = sort_model.sort_models(variable, 'ukv', files_ukv, disheight, z0zdlist, DOYstart, DOYstop,
                                 obs_site, saveyn,
                                 savepath, model_format)

    # define dict for included models
    included_models = {}
    group_ukv = [ukv[5], ukv[6], ukv[0], ukv[1], ukv[10]]
    # append to dict
    included_models['ukv'] = group_ukv

    # time series plot
    # times_series.time_series_plot(variable, saveyn, obs_site, DOYstart, DOYstop, savepath + 'all_', run,
    #                               included_models, group_obs)

    obs_time, obs_vals = array_retrieval.retrive_arrays_obs(group_obs)

    obs_time_par, obs_vals_par = array_retrieval.retrive_arrays_obs(group_obs_par)


    df = kdown_averages_tests.kdown_averages(obs_time, obs_vals, 60)
    obs_time = df.index
    obs_vals = df['vals']
    df_par = kdown_averages_tests.kdown_averages(obs_time_par, obs_vals_par, 60)
    obs_time_par = df_par.index
    obs_vals_par = df_par['vals']


    mod_time, mod_vals = array_retrieval.retrive_arrays_model(included_models, 'ukv')

    # kdown plot
    kdown_timeseries_tests.kdown_timeseries(obs_time, obs_vals, obs_time_par, obs_vals_par, mod_time, mod_vals, obs_site,
                     DOYstart, DOYstop, saveyn, savepath, variable)




    print('end')














########################################################################################################################
# c h o i c e s
DOYstart_choice = 2016201
DOYstop_choice = 2016201
sample = '15min'
obs_level = 'L1'
run = '21Z'
# For scintillometry, variable is always sensible heat currently - needn't ever change this
variable = 'kdown'

obs_site = 'IMU'
instrument = 'Davis'

file_format = ['old', 'new']
model_format = file_format[1]



if __name__ == "__main__":

    # Join list items using join()
    site_string = obs_site

    folder_name = str(DOYstart_choice) + '_' + str(DOYstop_choice) + '_' + variable + '_' + site_string + '_' + str(
        obs_site) + '/'
    save_folder = '../../plots/' + folder_name

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    main(obs_site, DOYstart_choice, DOYstop_choice, variable, save_folder, 1, run,
         instrument, sample, model_format, obs_level)

print(' ')
print(' ')
print('FINISH')






