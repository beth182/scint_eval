# function to look at observations in detail

from calendar import isleap
import os
import sys
import numpy as np
from scint_eval.functions import retrieve_var
from scint_eval.functions import plotting_funs
from scint_eval.functions import file_read

from scint_eval.functions import array_retrieval
from scint_eval.functions import sort_model
from scint_eval.functions import sort_model_wind
from scint_eval.functions import roughness
from scint_eval.functions import find_source_area
from scint_eval.functions import grid_percentages
from scint_eval import look_up
from scint_eval.functions import read_ceda_heathrow


def main(obs_site, DOYstart, DOYstop, variable, savepath, saveyn, run, instrument, sample,
         model_format, obs_level, scint_path):
    """
    MAIN FUNCTION FOR NEW FILE FORMAT MODEL FILES.
    """

    ################################################################################################################
    # finding observation files
    # file_read.py
    files_obs = file_read.finding_files(model_format, 'obs', DOYstart, DOYstop, obs_site, run, instrument, sample,
                                        variable, obs_level,
                                        obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/',
                                        # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )

    files_obs_10minsa = file_read.finding_files(model_format, 'obs', DOYstart, DOYstop, obs_site, run, instrument,
                                                '1min_sa10min',
                                                variable, obs_level,
                                                obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/',
                                                # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                                )

    all_days_vars = retrieve_var.retrive_var(files_obs,
                                             ['QH', 'wind_direction_corrected', 'wind_speed', 'wind_speed_adj', 'kdown',
                                              'z_0', 'z_d',
                                              'sa_area_km2', 'stab_param'])

    all_days_vars_10minsa = retrieve_var.retrive_var(files_obs_10minsa,
                                                     ['QH', 'wind_direction_corrected', 'wind_speed', 'wind_speed_adj',
                                                      'kdown', 'z_0', 'z_d',
                                                      'sa_area_km2', 'stab_param'])

    ###########################
    # DOY 142
    files_obs_123 = file_read.finding_files(model_format, 'obs', 2016123, 2016123, obs_site, run, instrument, sample,
                                            variable, obs_level,
                                            obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/',
                                            # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                            )

    files_obs_10minsa_123 = file_read.finding_files(model_format, 'obs', 2016123, 2016123, obs_site, run, instrument, '1min_sa10min',
                                        variable, obs_level,
                                                    obs_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/',
                                        # obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/"
                                        )

    all_days_vars_123 = retrieve_var.retrive_var(files_obs_123,
                                             ['QH', 'wind_direction_corrected', 'wind_speed_adj', 'kdown', 'z_0', 'z_d',
                                              'sa_area_km2', 'stab_param'])

    all_days_vars_10minsa_123 = retrieve_var.retrive_var(files_obs_10minsa_123,
                                                     ['QH', 'wind_direction_corrected', 'wind_speed_adj', 'kdown', 'z_0', 'z_d',
                                                      'sa_area_km2', 'stab_param'])

    ###########################
    # deal with the stupid key system
    all_days_vars_123 = all_days_vars_123['obs2016123']
    all_days_vars_10minsa_123 = all_days_vars_10minsa_123['obs2016_sa']

    all_days_vars = all_days_vars['obs' + str(DOYstart)]
    all_days_vars_10minsa = all_days_vars_10minsa['obs2016_sa']

    ####################################################################################################################
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

    # define roughness and displacemet
    # roughness.py
    # note: this step doesn't matter with the scint runs. As we are evaluating a surface model output.
    # This step is only included to keep things running, and values are over-written in the sort_model function.
    z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                    look_up.obs_zd_macdonald[obs_site])

    ####################################################################################################################
    # WIND
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

    # calculate height and adjust for roughness length
    av_10min_zf = np.nanmean(all_days_vars_10minsa['z_f'])
    av_10min_z0 = np.nanmean(all_days_vars_10minsa['z_0'])
    av_disheight = av_10min_zf - av_10min_z0

    ukv_wind = sort_model_wind.sort_models_wind('wind', 'ukv', files_ukv_wind, av_disheight, DOYstart, DOYstop,
                                                'BCT', savepath, model_format, grid_choice='E')

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

    # """

    ####################################################################################################################
    # KDOWN
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
    # """

    # """
    ####################################################################################################################

    # QH

    if DOYstart == 2016118:
        sa_hours_avail = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]  # 11

    elif DOYstart == 2016142:
        sa_hours_avail = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 142

    elif DOYstart == 2016111:
        sa_hours_avail = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    elif DOYstart == 2016126:
        sa_hours_avail = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]  # 126
    elif DOYstart == 2016123:
        sa_hours_avail = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]  # 123
    else:
        print('make a doy choice w/ sas')
        sys.exit()

    time = []
    for hour in all_days_vars['time']:
        if hour.hour in sa_hours_avail:
            new_time = hour.replace(minute=0, second=0, microsecond=0)
            print(new_time)

            time.append(new_time)

    time = sorted(list(set(time)))

    # find source area raster

    sa_in_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/' + str(DOYstart)[-3:] + '/hourly/'

    sa_list = find_source_area.find_source_area(time=time,
                                                in_dir=sa_in_dir)

    model_site_dict, percentage_vals_dict, percentage_covered_by_model = grid_percentages.prepare_model_grid_percentages(
        time=time,
        sa_list=sa_list,
        savepath=savepath)

    included_grids, model_site = grid_percentages.determine_which_model_files(model_site_dict, DOYstart_mod,
                                                                              DOYstop_mod, run,
                                                                              instrument,
                                                                              sample, variable,
                                                                              obs_level, model_format, 0,
                                                                              z0zdlist, saveyn,
                                                                              savepath)

    included_grids = grid_percentages.average_model_grids(included_grids, DOYstart_mod, DOYstop_mod,
                                                          percentage_vals_dict, model_site_dict, model_site)

    model_grid_vals = {}
    model_grid_time = {}

    for grid_choice in included_grids.keys():
        mod_time, mod_vals = array_retrieval.retrive_arrays_model(included_grids, grid_choice)

        model_grid_vals[grid_choice] = mod_vals
        model_grid_time[grid_choice] = mod_time

    mod_time_qh_wav = model_grid_time['WAverage']
    mod_vals_qh_wav = model_grid_vals['WAverage']

    # """

    print('here')

    # get heathrow winds
    heath_df = read_ceda_heathrow.read_ceda_heathrow(
        'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/Heathrow Mean Wind/station_data-201601010000-201612312359_w.csv',
        DOYstart)

    # get LC WD
    LC_df = read_ceda_heathrow.read_NOAA_LCairport(
        'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/London_city_2016_03768399999.csv',
        DOYstart)

    SWT_df = read_ceda_heathrow.read_SWT_sheet(
        'C:/Users/beths/OneDrive - University of Reading/London_2016_wind_obs/SWT_Weather_Data_2016.csv',
        DOYstart)

    print('here here')

    plotting_funs.plots_vars_mod(all_days_vars, all_days_vars_10minsa,
                                 mod_time_kdown, mod_vals_kdown,
                                 mod_time_ws, mod_vals_ws,
                                 mod_time_wd, mod_vals_wd,
                                 mod_time_qh_wav, mod_vals_qh_wav,
                                 heath_df,
                                 savepath)

    plotting_funs.QH_over_Kdn(all_days_vars, all_days_vars_10minsa,
                              mod_time_kdown, mod_vals_kdown,
                              mod_time_ws, mod_vals_ws,
                              mod_time_wd, mod_vals_wd,
                              mod_time_qh_wav, mod_vals_qh_wav,
                              heath_df,
                              savepath)

    print('end')

    # plot wind direction

    assert mod_time_ws.all() == mod_time_wd.all() == mod_time_ws0.all() == mod_time_wd0.all() == mod_time_ws2.all() == mod_time_wd2.all()

    plotting_funs.plot_wind_eval(all_days_vars, all_days_vars_10minsa,
                                 mod_time_ws, mod_vals_ws, mod_vals_wd, ukv_wind[6],
                                 mod_vals_ws0, mod_vals_wd0, ukv_wind[14],
                                 mod_vals_ws2, mod_vals_wd2, ukv_wind[15],
                                 heath_df, LC_df, SWT_df,
                                 savepath)

    print('end')

    ###########################
    # plots

    # plotting_funs.plots_vars(all_days_vars, all_days_vars_10minsa)

    # plotting_funs.qh_comparison(all_days_vars, all_days_vars_10minsa)

    # plotting_funs.qh_vs_zf(all_days_vars, all_days_vars_10minsa)

    plotting_funs.qh_vs_zf_both_days(all_days_vars, all_days_vars_10minsa, all_days_vars_123, all_days_vars_10minsa_123)

    # plotting_funs.find_mean_zf(all_days_vars_10minsa)

    # plotting_funs.find_mean_zf_both_days(all_days_vars_10minsa, all_days_vars_10minsa_142)

    # plotting_funs.qh_vs_zf_hour_mean(all_days_vars_10minsa)

    # plotting_funs.qh_vs_zf_day_mean(all_days_vars_10minsa)

    plotting_funs.qh_vs_zf_day_mean_both_days(all_days_vars_10minsa, all_days_vars_10minsa_123)

    print('END')


########################################################################################################################
# c h o i c e s
# CHANGE HERE

DOYstart_choice = 2016126
DOYstop_choice = 2016126

# DOYstart_choice = 2016142
# DOYstop_choice = 2016142

# DOYstart_choice = 2016111
# DOYstop_choice = 2016111

# DOYstart_choice = 2016118
# DOYstop_choice = 2016118

sample = '1min'
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
