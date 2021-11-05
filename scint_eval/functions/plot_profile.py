import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from matplotlib.dates import DateFormatter
import netCDF4 as nc
import pylab
from matplotlib import pyplot
import sys

from scint_eval import look_up
from scint_eval.functions import tools
from scint_eval.functions import plotting_funs

mpl.use('TkAgg')


# ----------------------------------------------------------------------------------------------------------------------
def plot_model_profile(variable,
                       file,
                       grid_choice,
                       savepath,
                       obs_file,
                       surface_file):



    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    modlon_ncfile = nc.Dataset(file)
    modlon_ncfile_surf = nc.Dataset(surface_file)

    var = modlon_ncfile.variables['boundary_layer_heat_fluxes']
    var_surf = modlon_ncfile_surf.variables['surface_sensible_heat_flux']

    ####################################################################################################################
    # GRID FAFF
    if grid_choice == 0:
        # Defult val goes to centre grid, otherwise known as grid 'E':
        index_lat = 1
        index_lon = 1
    elif grid_choice == 'A':
        index_lat = 2
        index_lon = 0
    elif grid_choice == 'B':
        index_lat = 2
        index_lon = 1
    elif grid_choice == 'C':
        index_lat = 2
        index_lon = 2
    elif grid_choice == 'D':
        index_lat = 1
        index_lon = 0

    elif grid_choice == 'E':
        index_lat = 1
        index_lon = 1

    elif grid_choice == 'F':
        index_lat = 1
        index_lon = 2
    elif grid_choice == 'G':
        index_lat = 0
        index_lon = 0
    elif grid_choice == 'H':
        index_lat = 0
        index_lon = 1
    elif grid_choice == 'I':
        index_lat = 0
        index_lon = 2
    ####################################################################################################################

    ####################################################################################################################
    # TIME FAFF
    modstarttimelon = modlon_ncfile.variables['time'].units
    mod_time_sincelon = [np.squeeze(modlon_ncfile.variables['forecast_reference_time'])]
    mod_time_startlon = tools.time_to_datetime(modstarttimelon, mod_time_sincelon)[0]
    mod_time_forecastlon = np.squeeze(modlon_ncfile.variables['forecast_period'][:])
    modtimelon = [mod_time_startlon + dt.timedelta(seconds=hr * 3600) for hr in mod_time_forecastlon]
    start_index = -33
    end_index = -25
    midnight_date = dt.datetime.strptime(str(file[start_index:end_index]), '%Y%m%d') + dt.timedelta(
        days=1)
    midnight = dt.time(0, 0)
    midnight_datetime = dt.datetime.combine(midnight_date, midnight)
    # constructing 21 Z
    correct_date = dt.datetime.strptime(str(file[start_index:end_index]), '%Y%m%d')
    correct_time = dt.time(21, 0)
    correct_datetime = dt.datetime.combine(correct_date, correct_time)
    # constructing 10 pm
    # seen in lon files
    ten_date = dt.datetime.strptime(str(file[start_index:end_index]), '%Y%m%d')
    ten_time = dt.time(22, 0)
    ten_datetime = dt.datetime.combine(ten_date, ten_time)
    # if the time isn't exactly on the hour
    if modtimelon[0].minute != 0 or modtimelon[0].second != 0 or modtimelon[0].microsecond != 0:
        for i, item in enumerate(modtimelon):
            # Rounds to nearest hour by adding a timedelta hour if minute >= 30
            new_t = item.replace(second=0, microsecond=0, minute=0, hour=item.hour) + dt.timedelta(
                hours=item.minute // 30)
            # if the difference between the time and the nearest hour is less than a minute and a half:
            if abs(item - new_t) < dt.timedelta(minutes=1.5):
                modtimelon[i] = new_t
            else:
                print('problem')
                print('end')
    # does the model times start where it should? should start at 9, and I want to take all values from after
    # the first 3 hours (allowing for spin up) - so ideally times should start at midnight for a perfect file
    if modtimelon[0] == correct_datetime:
        # index to start defined here, as different situations have a different start index.
        # and these need to be considered when taking values, too. Otherwise, list lengths will be different.
        index_to_start = 3
    # if the file starts at midnight, don't need to adjust for spin up (as this is already not taking first
    # 3 hours)
    elif modtimelon[0] == midnight_datetime:
        index_to_start = 0
    # some files start at 10 pm? so therefore neglect forst 2 hours instead of 3 hours
    elif modtimelon[0] == ten_datetime:
        index_to_start = 2
    else:
        print('problem')
        print('end')
    modtimeslon = modtimelon[index_to_start:index_to_start + 24]
    ####################################################################################################################

    ####################################################################################################################
    # HEIGHT FAFF
    modheightlon = modlon_ncfile.variables['level_height'][:]

    ####################################################################################################################

    # colours ##############################################################################################################
    cmap = plt.cm.rainbow  # define the colormap
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]

    list_len = len(modtimeslon)

    colour_len = len(cmaplist)

    colour_intervals = int(colour_len / list_len)

    colour_list = []

    count = 0
    for i in modtimeslon:
        color_choice = cmaplist[count]
        colour_list.append(color_choice)
        count += colour_intervals

    plt.figure(figsize=(10, 10))

    # grid_latitude, grid_longitude, time, model_level_number
    var_grid = var[index_lat, index_lon, index_to_start:index_to_start + 24, :]
    var_surf_grid = var_surf[index_lat, index_lon, index_to_start:index_to_start + 24]

    for i in range(len(modtimeslon)):
        qh_at_1_time = var_grid[i, :]

        plt.plot(qh_at_1_time, modheightlon, label=str(i), color=colour_list[i], marker='.')


    # read observation file
    obs_ncfile = nc.Dataset(obs_file)
    z_f = obs_ncfile.variables['z_f'][:]
    max_z_f = np.nanmax(z_f)
    min_z_f = np.nanmin(z_f)
    plt.axhspan(min_z_f, max_z_f, alpha=0.2, color='red')

    plt.scatter(var_surf_grid, np.zeros(len(var_surf_grid)), color='k', marker='x')

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 10})
    plt.ylim(-10, 150)
    plt.xlim(-50, 200)
    plt.ylabel('z (m)')
    plt.xlabel(label_string)
    plt.savefig(savepath + 'yeeeeee.png')

    print('end')
