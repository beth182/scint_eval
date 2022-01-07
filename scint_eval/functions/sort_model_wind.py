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

# plt.switch_backend('agg')
# mpl.rcParams.update({'font.size': 20})  # updating the matplotlib fontsize


# ----------------------------------------------------------------------------------------------------------------------
def sort_models_wind(variable,
                     model,
                     files,
                     target_height,
                     DOYstart,
                     DOYstop,
                     sitechoice,
                     savestring,
                     MO_format,
                     grid_choice=0,
                     hoursbeforerepeat=24):
    """
    :param variable: choice of variable. Entered as a string.
    Can so far be: 'Tair' or 'wind'
    :param model: choice of model. Entered as a string. Can be 'ukv' or 'lon' for the London model.
    :param files: From finding_files: 3 dictionaries of filepaths of data to be read in. Observations, London model
    and the ukv. Originally from the functions findfiles (for the cluster), and findfilesold (for laptop/desktop).
    :param disheight: Height of observation, given from the function observations, after adjusting for roughness length
    and displacement height. This is used to find the model level at which the comparison is being made.
    :param z0zd: List of different roughness lengths and displacement heights for the models and observations.
    :param DOYstart: date choices, where DOY is day of year. Start of date range.
    This is to be entered as a normal number, i.e. do not wrap
    one didget DOYs with 0's (example: DOY one is 1, and not 001).
    :param DOYstop: date choices, where DOY is day of year. End of date range. (Also, see above for DOYstart format).
    :param sitechoice: Choice of site.
    This is entered as a string.
    :param saveyn: decides whether to save a plot made, or show it.
    1 = save, 0 = show
    :param savestring: Where to save the plots produced.
    :param hoursbeforerepeat: this is used to get rid of the repeated items in the model plots - as, in each time,
    datetimes are repeated (as the model files aren't 24 hours, they're 37 hours, and are run again every 24 hours,
    leaving 13 hours of repeat each time).
    Entered as a number. Typically 24
    #ToDo: add in the MO_format here

    # if variable == wind:
    :return lontimedict: Dictionary of lists of time values for each file.
    :return lonwinddict: Dictionary of lists of wind speed values for each file.
    :return londirdict: Dictionary of lists of wind direction values for each file.
    :return stringtimelon: List of strings of keys in the lontimedict, to call in order when plotting.
    :return stringwindlon: List of strings of keys in the lonwinddict, to call in order when plotting.
    :return stringdirlon: List of strings of keys in the londirdict, to call in order when plotting.
    :return modheightvaluelon: Chosen model level height.
    :return alllontimes: List of all times included for all files.

    # if variable == something other than wind:
    (note, 'temp' is used here in variable names, but these don't have to be JUST temperature.
    :return lontimedict: Dictionary of lists of time values for each file.
    :return lontempdict: Dictionary of lists of variable chosen values for each file.
    :return lontempdict9: Dictionary of lists of variable chosen values for each file. - this is averaged over all 9
    grid boxes, to compare to the case of just the centre grid values.
    :return lontempdict0: Dictionary of lists of time values for each file. This is the level below the chosen
    model level.
    :return lontempdict2: Dictionary of lists of time values for each file. This is the level above the chosen model
    level.
    :return stringtimelon: List of strings of keys in the lontimedict, to call in order when plotting.
    :return stringtemplon: List of strings of keys in the lontempdict, to call in order when plotting.
    :return stringtemplon9: List of strings of keys in the lontempdict9, to call in order when plotting.
    :return stringtemplon0: List of strings of keys in the lontempdict0, to call in order when plotting.
    :return stringtemplon2: List of strings of keys in the lontempdict2, to call in order when plotting.
    :return modheightvaluelon: Chosen model level height.
    :return modheightvaluelon0: Height below chosen model level height.
    :return modheightvaluelon2: Height above chosen model level height.
    :return alllontimes: List of all times included for all files.

    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Sorting Model Wind: ' + str(model))
    print(' ')

    # if there are no model files
    if len(files) == 0:
        print('No files for model:', model)
        lontimedict = []
        lonwinddict = []
        londirdict = []
        stringtimelon = []
        stringwindlon = []
        stringdirlon = []
        modheightvaluelon = []
        alllontimes = []
        stringwindlon9 = []
        stringdirlon9 = []
        stringwindlon0 = []
        stringdirlon0 = []
        stringwindlon2 = []
        stringdirlon2 = []
        modheightvaluelon0 = []
        modheightvaluelon2 = []
        lonwinddict9 = []
        londirdict9 = []
        lonwinddict0 = []
        londirdict0 = []
        lonwinddict2 = []
        londirdict2 = []
        return (lontimedict,
                lonwinddict,
                londirdict,
                stringtimelon,
                stringwindlon,
                stringdirlon,
                modheightvaluelon,
                alllontimes,
                stringwindlon9,
                stringdirlon9,
                stringwindlon0,
                stringdirlon0,
                stringwindlon2,
                stringdirlon2,
                modheightvaluelon0,
                modheightvaluelon2,
                lonwinddict9,
                londirdict9,
                lonwinddict0,
                londirdict0,
                lonwinddict2,
                londirdict2)

    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    ####################################################################################################################
    #                                                     WIND
    ####################################################################################################################
    # MORE THAN ONE STASH CODE INCLUDED FOR THIS VARIABLE
    u_index_for_files = 0
    v_index_for_files = 1

    # creates lists to plot outside of the for loop
    lontimedict = {}
    for item in files[0].keys():
        varname = "time" + str(item)
        lontimedict[varname] = []
        lontimedict[varname].append('placeholder')
    # speed
    lonwinddict = {}
    for item in files[0].keys():
        varname = "wind" + str(item)
        lonwinddict[varname] = []
        lonwinddict[varname].append('placeholder')
    # dir
    londirdict = {}
    for item in files[0].keys():
        varname = "dir" + str(item)
        londirdict[varname] = []
        londirdict[varname].append('placeholder')

    # Creating a list to keep track of any dodgy model files with large time arrays when converting to datetime
    dodgeyfileslon = []

    # all 9 grids temp - to average all the grids, rather than just take the centre grid
    # all variables associated with this include '9' in the variable name, due to there being 9 grids
    lonwinddict9 = {}
    for item in files[0].keys():
        varname = "wind9" + str(item)
        lonwinddict9[varname] = []
        lonwinddict9[varname].append('placeholder')

    londirdict9 = {}
    for item in files[0].keys():
        varname = "dir9" + str(item)
        londirdict9[varname] = []
        londirdict9[varname].append('placeholder')

    # adding the height above and below:
    lonwinddict0 = {}
    for item in files[0].keys():
        varname = "wind0" + str(item)
        lonwinddict0[varname] = []
        lonwinddict0[varname].append('placeholder')
    lonwinddict2 = {}
    for item in files[0].keys():
        varname = "wind2" + str(item)
        lonwinddict2[varname] = []
        lonwinddict2[varname].append('placeholder')

    londirdict0 = {}
    for item in files[0].keys():
        varname = "dir0" + str(item)
        londirdict0[varname] = []
        londirdict0[varname].append('placeholder')
    londirdict2 = {}
    for item in files[0].keys():
        varname = "dir2" + str(item)
        londirdict2[varname] = []
        londirdict2[varname].append('placeholder')

    # loops over the london model file paths in obvsdict (to import the data each time), and the empty
    # lists ready in lonswinddict,and lontimedict, londirdict (plus 3x3 average and 2nd height lists)
    # these will be dictionaries including lists full of values and time respectively,
    # one list for each day/ file in the observation files
    for uitem, vitem, wind, time, direction, wind9, dir9, wind0, wind2, dir0, dir2 in zip(
            sorted(files[u_index_for_files].values()),
            sorted(files[v_index_for_files].values()),
            sorted(lonwinddict),
            sorted(lontimedict),
            sorted(londirdict),
            sorted(lonwinddict9),
            sorted(londirdict9),
            sorted(lonwinddict0),
            sorted(lonwinddict2),
            sorted(londirdict0),
            sorted(londirdict2)):

        # assigns model .nc file
        modlonpath = uitem
        modlonpathv = vitem

        # CHANGED 06/08/18 AS ONE OF THE FILES WAS CORRUPTED, AND COULDN'T BE READ BY NETCDF
        # modlon_ncfile = nc.Dataset(modlonpath)
        # modlon_ncfilev = nc.Dataset(modlonpathv)
        try:
            modlon_ncfile = nc.Dataset(modlonpath)
        except IOError:
            print('PROBLEM READING FILE:')
            print(modlonpath)
            print("It's size may be 0, and netCDF may have troubles opening corrupted file.")
            dodgeyfileslon.append(modlonpath)
            continue

        try:
            modlon_ncfilev = nc.Dataset(modlonpathv)
        except IOError:
            print('PROBLEM READING FILE:')
            print(modlonpath)
            print("It's size may be 0, and netCDF may have troubles opening corrupted file.")
            dodgeyfileslon.append(modlonpath)
            continue

        # reads in model height
        # Read in the model data heights. As data is 3x3 grid, take the central
        # cell which overlays the observation location.

        # finding the altitude from the model
        site_format = look_up.sites[sitechoice]
        # finds altitude from function
        altitude = look_up.find_altitude(site_format, model)


        if MO_format == 'old':
            modheightlon = modlon_ncfile.variables['height']
            modheightlistlon = modheightlon[:, 1, 1] + altitude

        elif MO_format == 'new':

            try:
                modheightlon = modlon_ncfile.variables['level_height']
                modheightlistlon = modheightlon[:] + altitude

            except KeyError as error:
                dodgeyfileslon.append(modlonpath)
                print(' ')
                print('ERROR HERE: ', modlonpath)
                print("Could not read in ", error, " as this is not a variable in the file")
                print(' ')
                continue

            # tests to make sure all files with just one variable (and not time/ height) are caught
            try:
                modheightlonv = modlon_ncfilev.variables['level_height']
            except KeyError as error:
                dodgeyfileslon.append(modlonpathv)
                print(' ')
                print('ERROR HERE: ', modlonpathv)
                print("Could not read in ", error, " as this is not a variable in the file")
                print(' ')
                continue

        else:
            print('MO_format not an option.')
            sys.exit()

        # finds the closest value of model height to observation, and saves the index
        # if there is no observation files, disheight will be returned as an empty list. So this list is replaced by
        # 10 m, in order to still plot model files if they exist.
        if target_height == []:
            target_height = 10

        # why am I doing this in this funtion?
        # should be removed and done outside

        # where model_options[model][2] is z0_index
        # z0_index = look_up.model_options[model][2]
        # heightindexlon = np.abs(modheightlistlon - (disheight + z0zd[z0_index])).argmin()

        heightindexlon = np.abs(modheightlistlon - target_height).argmin()

        # if 1D, won't have to unravel
        modheightvaluelon = modheightlistlon[heightindexlon]

        # taking the next closest heights
        heightindexlon0 = heightindexlon - 1
        heightindexlon2 = heightindexlon + 1
        modheightvaluelon0 = modheightlistlon[heightindexlon0]
        modheightvaluelon2 = modheightlistlon[heightindexlon2]


        # reads in time
        if MO_format == 'new':
            # KSSW is a site with more letters than others, so it's handled differently when finding the date:
            if sitechoice == 'KSSW':
                start_index = -34
                end_index = -26
            elif sitechoice == 'BFCL':
                start_index = -34
                end_index = -26
            elif sitechoice == 'MR':
                start_index = -32
                end_index = -24
            elif sitechoice == 'NK':
                start_index = -32
                end_index = -24
            else:
                start_index = -33
                end_index = -25
        elif MO_format == 'old':
            start_index = 71
            end_index = 79
        else:
            print('File type given neither new or old.')
            sys.exit()

        # DIFFERENT LENGTHS OF FILES...

        # constructing midnight
        # seen in ukv files
        midnight_date = dt.datetime.strptime(str(modlonpath[start_index:end_index]), '%Y%m%d') + dt.timedelta(
            days=1)
        midnight = dt.time(0, 0)
        midnight_datetime = dt.datetime.combine(midnight_date, midnight)

        # constructing 21 Z
        correct_date = dt.datetime.strptime(str(modlonpath[start_index:end_index]), '%Y%m%d')
        correct_time = dt.time(21, 0)
        correct_datetime = dt.datetime.combine(correct_date, correct_time)

        # constructing 10 pm
        # seen in lon files
        ten_date = dt.datetime.strptime(str(modlonpath[start_index:end_index]), '%Y%m%d')
        ten_time = dt.time(22, 0)
        ten_datetime = dt.datetime.combine(ten_date, ten_time)

        # NEED TO DO TIMES TWICE FOR BOTH STASH CODE FILES TO SEE IF I HAVE THE SAME TIMES!
        # ----------------------------------------------------------------------------------------------------------
        # U
        # get time units for time conversion and start time
        modstarttimelon = modlon_ncfile.variables['time'].units

        # Read in minutes since the start time and add it on
        # Note: time_to_datetime needs time_since to be a list. Hence put value inside a single element list first

        if MO_format == 'old':
            mod_time_sincelon = [np.squeeze(modlon_ncfile.variables['time'])]
        elif MO_format == 'new':
            mod_time_sincelon = [np.squeeze(modlon_ncfile.variables['forecast_reference_time'])]
        else:
            print('MO_format not an option.')
            sys.exit()

        # create start time for model data
        # time_to_datetime outputs a list of datetimes, so remove the single element from the list.
        # time to datetime is an imported function
        # Having to put a try/except in here, because some of the model files are dodgey and gove huge time arrays
        # when converting to datetime
        try:
            mod_time_startlon = tools.time_to_datetime(modstarttimelon, mod_time_sincelon)[0]  # time_to_datetime is a
            # function defined at top
        except:
            dodgeyfileslon.append(modlonpath)
            print('DODGEY FILE: TIME ARRAY NOT AS EXPECTED: ', np.shape(modstarttimelon))
            continue

        # get number of forecast hours to add onto time_start
        if MO_format == 'old':
            mod_time_forecastlon = np.squeeze(modlon_ncfile.variables['forecast'][:])
        elif MO_format == 'new':
            mod_time_forecastlon = np.squeeze(modlon_ncfile.variables['forecast_period'][:])
        else:
            print('MO_format is not an option.')
            sys.exit()

        modtimelon = [mod_time_startlon + dt.timedelta(seconds=hr * 3600) for hr in mod_time_forecastlon]



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
                    print('ERROR: DODGEY FILE: ', modlonpath)
                    print('THERE IS A TIME WITH A LARGER DIFFERENCE THAN 1.5 MINUTES TO THE HOUR: ', item)
                    dodgeyfileslon.append(modlonpath)
                    continue

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
            print(' ')
            print('ERROR: DODGEY FILE: previously unseen time length in this file: ', modlonpath)
            print(len(modtimelon), 'start:', modtimelon[0], 'end:', modtimelon[-1])
            print(' ')
            dodgeyfileslon.append(modlonpath)
            continue

        modtimeslon = modtimelon[index_to_start:index_to_start+hoursbeforerepeat]

        # check to see if all hours are consecutive by 1 hour...
        flag = 0
        for i in range(0, len(modtimeslon) - 1):
            if modtimeslon[i + 1] == modtimeslon[i] + dt.timedelta(hours=1):
                pass
            else:
                print(' ')
                print('ERROR: There is a jump in hours: ')
                print(modtimeslon[i], modtimeslon[i + 1])
                print('For file: ' + modlonpath)

                flag = 1

        if flag == 1:
            dodgeyfileslon.append(modlonpath)
            continue

        # ----------------------------------------------------------------------------------------------------------
        # V
        # get time units for time conversion and start time
        modstarttimelonv = modlon_ncfilev.variables['time'].units

        # Read in minutes since the start time and add it on
        # Note: time_to_datetime needs time_since to be a list. Hence put value inside a single element list first

        if MO_format == 'old':
            mod_time_sincelonv = [np.squeeze(modlon_ncfilev.variables['time'])]
        elif MO_format == 'new':
            mod_time_sincelonv = [np.squeeze(modlon_ncfilev.variables['forecast_reference_time'])]
        else:
            print('MO_format not an option.')
            sys.exit()

        # create start time for model data
        # time_to_datetime outputs a list of datetimes, so remove the single element from the list.
        # time to datetime is an imported function
        # Having to put a try/except in here, because some of the model files are dodgey and gove huge time arrays
        # when converting to datetime
        try:
            mod_time_startlonv = tools.time_to_datetime(modstarttimelonv, mod_time_sincelonv)[0]  # time_to_datetime is a
            # function defined at top
        except:
            dodgeyfileslon.append(modlonpathv)
            print('DODGEY FILE: TIME ARRAY NOT AS EXPECTED: ', np.shape(modstarttimelonv))
            continue

        # get number of forecast hours to add onto time_start
        if MO_format == 'old':
            mod_time_forecastlonv = np.squeeze(modlon_ncfilev.variables['forecast'][:])
        elif MO_format == 'new':
            mod_time_forecastlonv = np.squeeze(modlon_ncfilev.variables['forecast_period'][:])
        else:
            print('MO_format is not an option.')
            sys.exit()

        modtimelonv = [mod_time_startlonv + dt.timedelta(seconds=hr * 3600) for hr in mod_time_forecastlonv]

        # if the time isn't exactly on the hour
        if modtimelonv[0].minute != 0 or modtimelonv[0].second != 0 or modtimelonv[0].microsecond != 0:
            for i, item in enumerate(modtimelonv):
                # Rounds to nearest hour by adding a timedelta hour if minute >= 30
                new_t = item.replace(second=0, microsecond=0, minute=0, hour=item.hour) + dt.timedelta(
                    hours=item.minute // 30)

                # if the difference between the time and the nearest hour is less than a minute and a half:
                if abs(item - new_t) < dt.timedelta(minutes=1.5):
                    modtimelonv[i] = new_t
                else:
                    print('ERROR: DODGEY FILE: ', modlonpathv)
                    print('THERE IS A TIME WITH A LARGER DIFFERENCE THAN 1.5 MINUTES TO THE HOUR: ', item)
                    dodgeyfileslon.append(modlonpathv)
                    continue

        # does the model times start where it should? should start at 9, and I want to take all values from after
        # the first 3 hours (allowing for spin up) - so ideally times should start at midnight for a perfect file
        if modtimelonv[0] == correct_datetime:
            # index to start defined here, as different situations have a different start index.
            # and these need to be considered when taking values, too. Otherwise, list lengths will be different.
            index_to_startv = 3
        # if the file starts at midnight, don't need to adjust for spin up (as this is already not taking first
        # 3 hours)
        elif modtimelonv[0] == midnight_datetime:
            index_to_startv = 0
        # some files start at 10 pm? so therefore neglect forst 2 hours instead of 3 hours
        elif modtimelonv[0] == ten_datetime:
            index_to_startv = 2

        else:
            print(' ')
            print('ERROR: DODGEY FILE: previously unseen time length in this file: ', modlonpathv)
            print(len(modtimelonv), 'start:', modtimelonv[0], 'end:', modtimelonv[-1])
            print(' ')
            dodgeyfileslon.append(modlonpathv)
            continue

        modtimeslonv = modtimelonv[index_to_startv:index_to_startv+hoursbeforerepeat]

        # check to see if all hours are consecutive by 1 hour...
        flag = 0
        for i in range(0, len(modtimeslonv) - 1):
            if modtimeslonv[i + 1] == modtimeslonv[i] + dt.timedelta(hours=1):
                pass
            else:
                print(' ')
                print('ERROR: There is a jump in hours: ')
                print(modtimeslonv[i], modtimeslonv[i + 1])
                print('For file: ' + modlonpathv)

                flag = 1

        if flag == 1:
            dodgeyfileslon.append(modlonpathv)
            continue

        # ----------------------------------------------------------------------------------------------------------
        # TIME TESTS BETWEEN THE TWO LISTS TO SEE IF THEY ARE THE SAME
        # if the 2 time lists start at the same time:
        if modtimeslon[0] == modtimeslonv[0]:
            # if the 2 lists are the same length
            if len(modtimeslon) == len(modtimeslonv):
                time_test_pass = True
            # if the two lists are not the same length
            else:
                time_test_pass = False
                # find all the indexes of items that are in one list but not the other
                # first way round
                index_list_uv = []
                for i, item in enumerate(modtimeslon):
                    if item in modtimeslonv:
                        pass
                    else:
                        index_list_uv.append(i)
                # second way round
                index_list_vu = []
                for i, item in enumerate(modtimeslonv):
                    if item in modtimeslon:
                        pass
                    else:
                        index_list_vu.append(i)

                # if both lists have items in the index list, there is a problem
                if len(index_list_uv) != 0 and len(index_list_vu) != 0:
                    print("Both time lists have items that the other one doesn't!")
                    sys.exit()

                # define the first index of an item that is on one and not the other
                if len(index_list_uv) == 0:
                    pass
                else:
                    index_diff = index_list_uv[0]

                if len(index_list_vu) == 0:
                    pass
                else:
                    index_diff = index_list_vu[0]

        else:
            print('The two time lists do not start with the same time!')
            print(modtimeslon[0], modtimeslonv[0])
            sys.exit()

        # ----------------------------------------------------------------------------------------------------------
        # Makes a choice about which grid to use. For NEW file format:
        # Defult grid choice is always 0 - this means centre grid is chosen (lat and lon idex both 1 - middle of 3x3
        # of it's a letter, grid lon and lat defined here:
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

        # ----------------------------------------------------------------------------------------------------------

        # READS IN VALUES
        # reads in u and v components of wind speed and direction
        if MO_format == 'old':
            modulon = modlon_ncfile.variables['U_m']
            modvlon = modlon_ncfile.variables['V_m']

            # finds wind values at the closest model height to obs
            moduvalueslon = modulon[0, index_to_start:, heightindexlon, 1, 1]
            modvvalueslon = modvlon[0, index_to_start:, heightindexlon, 1, 1]

            # taking the next closest heights
            moduvalueslon0 = modulon[0, index_to_start:, heightindexlon0, 1, 1]
            moduvalueslon2 = modulon[0, index_to_start:, heightindexlon2, 1, 1]
            modvvalueslon0 = modvlon[0, index_to_start:, heightindexlon0, 1, 1]
            modvvalueslon2 = modvlon[0, index_to_start:, heightindexlon2, 1, 1]

        elif MO_format == 'new':
            modulon = modlon_ncfile.variables['eastward_wind']
            modvlon = modlon_ncfilev.variables['northward_wind']

            # finds wind values at the closest model height to obs
            moduvalueslon = modulon[index_lat, index_lon, index_to_start:index_to_start+hoursbeforerepeat, heightindexlon]
            modvvalueslon = modvlon[index_lat, index_lon, index_to_start:index_to_start+hoursbeforerepeat, heightindexlon]

            # taking the next closest heights
            moduvalueslon0 = modulon[index_lat, index_lon, index_to_start:index_to_start+hoursbeforerepeat, heightindexlon0]
            moduvalueslon2 = modulon[index_lat, index_lon, index_to_start:index_to_start+hoursbeforerepeat, heightindexlon2]
            modvvalueslon0 = modvlon[index_lat, index_lon, index_to_start:index_to_start+hoursbeforerepeat, heightindexlon0]
            modvvalueslon2 = modvlon[index_lat, index_lon, index_to_start:index_to_start+hoursbeforerepeat, heightindexlon2]

        else:
            print('MO_format not an option.')
            sys.exit()

        # calculates wind speed and direction from u and v componants

        if time_test_pass == True:
            pass
        else:
            modvvalueslon = modvvalueslon[:index_diff - 1]
            moduvalueslon = moduvalueslon[:index_diff - 1]

        modwindlon = ((moduvalueslon ** 2) + (modvvalueslon ** 2)) ** 0.5
        # http://weatherclasses.com/uploads/4/2/8/6/4286089/computing_wind_direction_and_speed_from_u_and_v.pdf
        moddirlon = np.arctan2(moduvalueslon, modvvalueslon) * (180.0 / np.pi) + 180.0

        # Ensuring the direction is between 0 and 360 degrees
        for i in range(len(moddirlon)):
            if moddirlon[i] < 0.0:
                moddirlon[i] = moddirlon[i] + 360.0
            if moddirlon[i] > 360.0:
                moddirlon[i] = moddirlon[i] - 360.0

        # other heights:
        modwindlon0 = ((moduvalueslon0 ** 2) + (modvvalueslon0 ** 2)) ** 0.5
        moddirlon0 = np.arctan2(moduvalueslon0, modvvalueslon0) * (180.0 / np.pi) + 180.0
        for i in range(len(moddirlon0)):
            if moddirlon0[i] < 0.0:
                moddirlon0[i] = moddirlon0[i] + 360.0
            if moddirlon0[i] > 360.0:
                moddirlon0[i] = moddirlon0[i] - 360.0

        modwindlon2 = ((moduvalueslon2 ** 2) + (modvvalueslon2 ** 2)) ** 0.5
        moddirlon2 = np.arctan2(moduvalueslon2, modvvalueslon2) * (180.0 / np.pi) + 180.0
        for i in range(len(moddirlon2)):
            if moddirlon2[i] < 0.0:
                moddirlon2[i] = moddirlon2[i] + 360.0
            if moddirlon2[i] > 360.0:
                moddirlon2[i] = moddirlon2[i] - 360.0


        # append times to a list to plot outside of the for loop
        for item in modtimeslon:
            lontimedict[time].append(item)
        # append winds to a list to plot outside of the for loop
        for item in modwindlon:
            lonwinddict[wind].append(item)
        # append direction to a list to plot outside of the for loop
        for item in moddirlon:
            londirdict[direction].append(item)

        # 3x3 grid average
        if MO_format == 'old':
            shape_number = 1
        elif MO_format == 'new':
            shape_number = 2
        else:
            print('MO_format is not an option.')
            sys.exit()

        modumeans = []
        modvmeans = []

        for i in range(index_to_start, np.shape(modulon)[shape_number]):
            if MO_format == 'old':
                modumean = np.mean(modulon[0, i, heightindexlon, :, :])
                modvmean = np.mean(modvlon[0, i, heightindexlon, :, :])
            elif MO_format == 'new':
                modumean = np.mean(modulon[:, :, i, heightindexlon])
                modvmean = np.mean(modvlon[:, :, i, heightindexlon])
            else:
                'MO_format is not an option.'
                sys.exit()

            modumeans.append(modumean)
            modvmeans.append(modvmean)

        # calculates wind speed and direction from u and v components
        modwindvalueslonmean = []
        moddirvalueslonmean = []
        for umean, vmean in zip(modumeans, modvmeans):
            modwindvalueslonmeani = ((umean ** 2) + (vmean ** 2)) ** 0.5
            moddirvalueslonmeani = np.arctan2(umean, vmean) * (180.0 / np.pi) + 180.0
            # Ensuring the direction is between 0 and 360 degrees
            if moddirvalueslonmeani < 0.0:
                moddirvalueslonmeani = moddirvalueslonmeani + 360.0
            if moddirvalueslonmeani > 360.0:
                moddirvalueslonmeani = moddirvalueslonmeani - 360.0

            modwindvalueslonmean.append(modwindvalueslonmeani)
            moddirvalueslonmean.append(moddirvalueslonmeani)

        # append averages to a list to plot outside of the for loop
        lonwinddict9[wind9].append(modwindvalueslonmean)
        londirdict9[dir9].append(moddirvalueslonmean)

        # taking the next closest heights
        for item0 in modwindlon0:
            lonwinddict0[wind0].append(item0)
        for item2 in modwindlon2:
            lonwinddict2[wind2].append(item2)
        for item0 in moddirlon0:
            londirdict0[dir0].append(item0)
        for item2 in moddirlon2:
            londirdict2[dir2].append(item2)

    # print out any dodgey model files with huge time array lengths...
    print('number of dodgey model files:', len(dodgeyfileslon))
    if len(dodgeyfileslon) == 0:
        pass
    else:
        print(dodgeyfileslon)

    # deletes placeholder
    for item in lonwinddict:
        if lonwinddict[item][0] == 'placeholder':
            del lonwinddict[item][0]
    for item in lontimedict:
        if lontimedict[item][0] == 'placeholder':
            del lontimedict[item][0]
    for item in londirdict:
        if londirdict[item][0] == 'placeholder':
            del londirdict[item][0]
    for item in lonwinddict9:
        if lonwinddict9[item][0] == 'placeholder':
            del lonwinddict9[item][0]
    for item in londirdict9:
        if londirdict9[item][0] == 'placeholder':
            del londirdict9[item][0]
    for item in lonwinddict0:
        if lonwinddict0[item][0] == 'placeholder':
            del lonwinddict0[item][0]
    for item in lonwinddict2:
        if lonwinddict2[item][0] == 'placeholder':
            del lonwinddict2[item][0]
    for item in londirdict0:
        if londirdict0[item][0] == 'placeholder':
            del londirdict0[item][0]
    for item in londirdict2:
        if londirdict2[item][0] == 'placeholder':
            del londirdict2[item][0]

    # names to use for plotting in order - otherwise strange lines appear all over the plot,
    # trying to link datetimes together
    stringtimelon = []
    for item in sorted(lontimedict):
        stringtimelon.append(item)
    stringwindlon = []
    for item in sorted(lonwinddict):
        stringwindlon.append(item)
    stringdirlon = []
    for item in sorted(londirdict):
        stringdirlon.append(item)
    stringwindlon9 = []
    for item in sorted(lonwinddict9):
        stringwindlon9.append(item)
    stringdirlon9 = []
    for item in sorted(londirdict9):
        stringdirlon9.append(item)
    stringwindlon0 = []
    for item in sorted(lonwinddict0):
        stringwindlon0.append(item)
    stringdirlon0 = []
    for item in sorted(londirdict0):
        stringdirlon0.append(item)
    stringwindlon2 = []
    for item in sorted(lonwinddict2):
        stringwindlon2.append(item)
    stringdirlon2 = []
    for item in sorted(londirdict2):
        stringdirlon2.append(item)

    # A test to see if there are any repeated times within the London model, as part of the
    # 'strange lines on plot' debugging
    alllontimes = []
    for item in stringtimelon:
        for time in lontimedict[item][:hoursbeforerepeat]:
            alllontimes.append(time)
    print(' ')
    print('Finding any duplicate times:')
    if len(set([x for x in alllontimes if alllontimes.count(x) > 1])) == 0:
        print('No duplicates')
    else:
        print(len(set([x for x in alllontimes if alllontimes.count(x) > 1])), 'Duplicates')
        print(set([x for x in alllontimes if alllontimes.count(x) > 1]))

    # HEIGHT PROBLEM
    # remember that the label on the plots with height is the height of the centre grid, even for the
    # 3x3 averaged line
    if MO_format == 'old':
        modheightlistlonmeanlist = []
        findthebiggestdifflon = []
        biggestdifflevellon = []
        for i in range(0, 70):
            modheightlistlonmean = np.mean(modheightlon[i, :, :])
            modheightlistlonmeanlist.append(modheightlistlonmean)
            findthebiggestdifflon.append(abs(modheightlon[:, 1, 1][i] - modheightlistlonmeanlist[i]))
            biggestdifflevellon.append(modheightlon[:, 1, 1][i])

        modheightlistlon9 = np.asarray(modheightlistlonmeanlist)
        modheightvaluelon9 = modheightlistlon9[heightindexlon]

        print(' ')
        print('Finding the height differences:')
        print('the difference between the averaged 3x3 grid height and centre grid height: ' + str(
            abs(modheightvaluelon9 - modheightvaluelon)) + ' meters')

        print('the biggest difference in height is: ', max(
            findthebiggestdifflon), ' meters, occuring at height levels: ')

        biggestplaceslon = [i for i, x in enumerate(findthebiggestdifflon) if x == max(findthebiggestdifflon)]
        for item in biggestplaceslon:
            print(biggestdifflevellon[item])

    elif MO_format == 'new':
        pass
    else:
        print('MO_format not an option.')
        sys.exit()


    # dodgy files dealing with skipping times still for some reason appending the string name to string list. So here,
    # I am being lazy and manually removing any lists with time length 0 before plotting
    for wind, dir, windall, dirall, time in zip(stringwindlon, stringdirlon,
                                   stringwindlon9,stringdirlon9,
                                   stringtimelon
                                   ):

        if len(lontimedict[time][:hoursbeforerepeat]) == 0:
            print('There was a time list which has length 0: ', time)

            stringwindlon.remove(wind)
            stringwindlon9.remove(windall)
            stringdirlon.remove(dir)
            stringdirlon9.remove(dirall)
            stringtimelon.remove(time)

            # not sure I need these:
            del lontimedict[time]
            del lonwinddict[wind]
            del lonwinddict9[windall]
            del londirdict[dir]
            del londirdict9[dirall]

    # plotting the differences between 3x3 averaged and centre grid
    plt.figure(figsize=(20, 15))

    ax1 = pyplot.subplot(2, 1, 1)
    ax2 = pyplot.subplot(2, 1, 2)

    mod_colour = look_up.model_options[model][1]


    # for wind, time, direction in zip(stringwindlon9, stringtimelon, stringdirlon9):
    #     if len(lonwinddict9[wind]) > 0:
    #         plotCollection(ax1, lontimedict[time][:], lonwinddict9[wind][0][:],
    #                        'g')
    #
    #         plotCollection(ax2, lontimedict[time][:],
    #                        londirdict9[direction][0][:],
    #                        'g', label="3x3 averaged %s @ %d m" % (model, modheightvaluelon))


    for wind, time, direction in zip(stringwindlon, stringtimelon, stringdirlon):
        if len(lonwinddict[wind]) > 0:
            plotting_funs.plotCollection(ax1, lontimedict[time][:], lonwinddict[wind][:],
                           mod_colour)
            plotting_funs.plotCollection(ax2, lontimedict[time][:], londirdict[direction][:],
                           mod_colour, label="%s @ %d m" % (model, modheightvaluelon))

    # Try here because if one stash code is missing, plot can't be made (I think)
    # throws an error because 0 is not a date
    try:
        ax2.set_xlabel('DOY')
        ax1.set_ylabel(label_string[0])
        ax2.set_ylabel(label_string[1])
        ax2.xaxis.set_major_formatter(DateFormatter('%j'))

        date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
        plt.title(sitechoice + ': ' + date_for_title)

        plt.gcf().autofmt_xdate()

        pylab.savefig(savestring + str(variable) + '_' + str(model) + '_' + sitechoice + '_' +
                      str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')

    except:
        print('WIND PLOTS NOT MADE!!!')
        modheightvaluelon = 0
        modheightvaluelon0 = 0
        modheightvaluelon2 = 0

    return (lontimedict,
            lonwinddict,
            londirdict,
            stringtimelon,
            stringwindlon,
            stringdirlon,
            modheightvaluelon,
            alllontimes,
            stringwindlon9,
            stringdirlon9,
            stringwindlon0,
            stringdirlon0,
            stringwindlon2,
            stringdirlon2,
            modheightvaluelon0,
            modheightvaluelon2,
            lonwinddict9,
            londirdict9,
            lonwinddict0,
            londirdict0,
            lonwinddict2,
            londirdict2)
