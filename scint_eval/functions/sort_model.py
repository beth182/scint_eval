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

plt.switch_backend('agg')


# ----------------------------------------------------------------------------------------------------------------------
def sort_models(variable,
                model,
                files,
                disheight,
                z0zd,
                DOYstart,
                DOYstop,
                sitechoice,
                saveyn,
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
    print('Sorting Model: ' + str(model))
    print(' ')

    # if there are no model files
    if len(files) == 0:
        print('No files for model:', model)
        lontimedict = []
        lontempdict = []
        lontempdict9 = []
        lontempdict0 = []
        lontempdict2 = []
        stringtimelon = []
        stringtemplon = []
        stringtemplon9 = []
        stringtemplon0 = []
        stringtemplon2 = []
        modheightvaluelon = []
        modheightvaluelon0 = []
        modheightvaluelon2 = []
        alllontimes = []

        return (lontimedict,
                lontempdict,
                lontempdict9,
                lontempdict0,
                lontempdict2,
                stringtimelon,
                stringtemplon,
                stringtemplon9,
                stringtemplon0,
                stringtemplon2,
                modheightvaluelon,
                modheightvaluelon0,
                modheightvaluelon2,
                alllontimes)

    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    ####################################################################################################################
    #                                                     SORT MODELS
    ####################################################################################################################
    # creates lists to plot outside of the for loop
    lontimedict = {}
    for item in files.keys():
        varname = "time" + str(item)
        lontimedict[varname] = []
        lontimedict[varname].append('placeholder')
    lontempdict = {}
    for item in files.keys():
        varname = "temp" + str(item)
        lontempdict[varname] = []
        lontempdict[varname].append('placeholder')

    # Creating a list to keep track of any dodgy model files with large time arrays when converting to datetime
    dodgeyfileslon = []

    # all 9 grids temp - to average all the grids, rather than just take the centre grid
    # all variables associated with this include '9' in the variable name, due to there being 9 grids
    lontempdict9 = {}
    for item in files.keys():
        varname = "temp9" + str(item)
        lontempdict9[varname] = []
        lontempdict9[varname].append('placeholder')

    # adding the height above and below:
    lontempdict0 = {}
    for item in files.keys():
        varname = "temp0" + str(item)
        lontempdict0[varname] = []
        lontempdict0[varname].append('placeholder')
    lontempdict2 = {}
    for item in files.keys():
        varname = "temp2" + str(item)
        lontempdict2[varname] = []
        lontempdict2[varname].append('placeholder')

    # loops over the london model file paths in obvsdict (to import the data each time), and the empty
    # lists ready in lonstempdict, lontempdict9 (for 3x3 average) and lontimedict
    # these will be dictionaries including lists full of values and time respectively,
    # one list for each day/ file in the observation files
    for item, temp, time, temp9, temp0, temp2 in zip(sorted(files.values()),
                                                     sorted(lontempdict),
                                                     sorted(lontimedict),
                                                     sorted(lontempdict9),
                                                     sorted(lontempdict0),
                                                     sorted(lontempdict2)):
        # assigns model .nc file
        modlonpath = item
        # CHANGED 06/08/18 AS ONE OF THE FILES WAS CORRUPTED, AND COULDN'T BE READ BY NETCDF
        try:
            modlon_ncfile = nc.Dataset(modlonpath)
            # print ' '
            # print modlon_ncfile.variables['air_temperature']
            # print ' '
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


        if variable == 'BL_H':

            modheightlon = modlon_ncfile.variables['level_height']
            modheightlistlon = modheightlon[:]



        else:

            if MO_format == 'old':
                modheightlon = modlon_ncfile.variables['height']
                modheightlistlon = modheightlon[:, 1, 1] + altitude

            elif MO_format == 'new':
                # model level variables
                if variable == 'Tair' or variable == 'RH' or variable == 'Press':

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

                # surface level variables
                elif variable == 'kdown' or variable == 'kup' or variable == 'ldown' or variable == 'lup' or variable == 'netallwave' or variable == 'H' or variable == 'LE':
                    modheightlon = np.zeros(70)
                    modheightlistlon = modheightlon[:] + altitude

            else:
                print('MO_format not an option.')
                sys.exit()

        # finds the closest value of model height to observation, and saves the index
        # if there is no observation files, disheight will be returned as an empty list. So this list is replaced by
        # 10 m, in order to still plot model files if they exist.
        if disheight == []:
            disheight = 10
        # where model_options[model][2] is z0_index
        z0_index = look_up.model_options[model][2]
        heightindexlon = np.abs(modheightlistlon - (disheight + z0zd[z0_index])).argmin()

        # if 1D, won't have to unravel: heightindex = np.unravel_index(heightindex, np.shape(modheight))
        modheightvaluelon = modheightlistlon[heightindexlon]

        # taking the next closest heights
        heightindexlon0 = heightindexlon - 1
        heightindexlon2 = heightindexlon + 1
        modheightvaluelon0 = modheightlistlon[heightindexlon0]
        modheightvaluelon2 = modheightlistlon[heightindexlon2]

        # reads in time
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

        modtimeslon = modtimelon[index_to_start:index_to_start + hoursbeforerepeat]

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

        # READS IN VALUES
        if variable == 'Tair':
            # reads in temperatures
            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['T_m']
                # finds temperature values at the closest model height to obs
                modtempvalueslon = modtemplon[0, index_to_start:, heightindexlon, 1, 1] - 273.15

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, heightindexlon0, 1, 1] - 273.15
                modtempvalueslon2 = modtemplon[0, index_to_start:, heightindexlon2, 1, 1] - 273.15

            elif MO_format == 'new':
                modtemplon = modlon_ncfile.variables['air_temperature']
                # finds temperature values at the closest model height to obs
                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                   heightindexlon] - 273.15

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                    heightindexlon0] - 273.15
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                    heightindexlon2] - 273.15

            else:
                print('MO_format not an option.')
                sys.exit()

        elif variable == 'RH':
            # reads in relative humidity
            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['RH']
                modtempvalueslon = modtemplon[0, index_to_start:, heightindexlon, 1, 1]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, heightindexlon0, 1, 1]
                modtempvalueslon2 = modtemplon[0, index_to_start:, heightindexlon2, 1, 1]

            elif MO_format == 'new':
                modtemplon = modlon_ncfile.variables['relative_humidity']

                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                   heightindexlon]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                    heightindexlon0]
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                    heightindexlon2]

            else:
                print('MO_format not an option.')
                sys.exit()

        elif variable == 'Press':
            # reads in Press
            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['P_thetaLev']
                modtempvalueslon = modtemplon[0, index_to_start:, heightindexlon, 1, 1] / 100.

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, heightindexlon0, 1, 1] / 100.
                modtempvalueslon2 = modtemplon[0, index_to_start:, heightindexlon2, 1, 1] / 100.

            elif MO_format == 'new':
                modtemplon = modlon_ncfile.variables['air_pressure']
                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                   heightindexlon] / 100.

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                    heightindexlon] / 100.
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                    heightindexlon] / 100.

            else:
                print('MO_format not an option.')
                sys.exit()

        elif variable == 'kdown':
            # reads in incoming shortwave radiation
            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['ASODW_S']
                modtempvalueslon = modtemplon[0, index_to_start:, 1, 1]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, 1, 1]
                modtempvalueslon2 = modtemplon[0, index_to_start:, 1, 1]

            elif MO_format == 'new':
                modtemplon = modlon_ncfile.variables['surface_downwelling_shortwave_flux_in_air']
                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            else:
                print('MO_format not an option.')
                sys.exit()

        elif variable == 'ldown':
            # reads in outgoing shortwave radiation
            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['ATHDW_S']
                modtempvalueslon = modtemplon[0, index_to_start:, 1, 1]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, 1, 1]
                modtempvalueslon2 = modtemplon[0, index_to_start:, 1, 1]

            elif MO_format == 'new':
                modtemplon = modlon_ncfile.variables['surface_downwelling_longwave_flux_in_air']
                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            else:
                print('MO_format not an option.')
                sys.exit()

        elif variable == 'lup':
            if MO_format == 'old':
                # reads in outgoing shortwave radiation
                modtemplon = modlon_ncfile.variables['ATHUP_S']
                modtempvalueslon = modtemplon[0, index_to_start:, 1, 1]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, 1, 1]
                modtempvalueslon2 = modtemplon[0, index_to_start:, 1, 1]

            elif MO_format == 'new':
                print(' ')
                print("LUP ISN'T POSSIBLE YET FOR NEW MO FORMAT!")
                sys.exit()

        elif variable == 'netallwave':
            if MO_format == 'old':
                # calculates net allwave radiation
                ldown = modlon_ncfile.variables['ATHDW_S']
                ldown_values = ldown[0, index_to_start:, 1, 1]

                lup = modlon_ncfile.variables['ATHUP_S']
                lup_values = lup[0, index_to_start:, 1, 1]

                kup = modlon_ncfile.variables['ASOUP_S']
                kup_values = kup[0, index_to_start:, 1, 1]

                kdown = modlon_ncfile.variables['ASODW_S']
                kdown_values = kdown[0, index_to_start:, 1, 1]

                modtempvalueslon = ldown_values - lup_values + kdown_values - kup_values

                # testing to see if kup is really k*
                """
                if model == 'ukv':
                    ldown = modlon_ncfile.variables['ATHDW_S']
                    ldown_values = ldown[0, index_to_start:, 1, 1]

                    lup = modlon_ncfile.variables['ATHUP_S']
                    lup_values = lup[0, index_to_start:, 1, 1]

                    kup = modlon_ncfile.variables['ASOUP_S']
                    kup_values = kup[0, index_to_start:, 1, 1]

                    kdown = modlon_ncfile.variables['ASODW_S']
                    kdown_values = kdown[0, index_to_start:, 1, 1]

                    modtempvalueslon = ldown_values - lup_values + kdown_values - kup_values

                if model == 'lon':
                    ldown = modlon_ncfile.variables['ATHDW_S']
                    ldown_values = ldown[0, index_to_start:, 1, 1]

                    lup = modlon_ncfile.variables['ATHUP_S']
                    lup_values = lup[0, index_to_start:, 1, 1]

                    kup = modlon_ncfile.variables['ASOUP_S']
                    kup_values = kup[0, index_to_start:, 1, 1]

                    kdown = modlon_ncfile.variables['ASODW_S']
                    kdown_values = kdown[0, index_to_start:, 1, 1]

                    kstar = kup[0, index_to_start:, 1, 1]
                    lstar = ldown_values - lup_values

                    modtempvalueslon = kstar + lstar

                """
                modtempvalueslon0 = modtempvalueslon
                modtempvalueslon2 = modtempvalueslon

                # used for the shape...
                modtemplon = modlon_ncfile.variables['ATHUP_S']

            elif MO_format == 'new':
                print(' ')
                print("QSTAR ISN'T POSSIBLE YET FOR NEW MO FORMAT!")
                sys.exit()


        elif variable == 'H':
            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['bl_hf']
                modtempvalueslon = modtemplon[0, index_to_start:, 0, 1, 1]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, 0, 1, 1]
                modtempvalueslon2 = modtemplon[0, index_to_start:, 0, 1, 1]

            elif MO_format == 'new':
                try:
                    modtemplon = modlon_ncfile.variables['surface_upward_sensible_heat_flux']
                except:
                    modtemplon = modlon_ncfile.variables['surface_sensible_heat_flux']
                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]


            else:
                print('MO_format not an option.')
                sys.exit()


        elif variable == 'BL_H':
            modtemplon = modlon_ncfile.variables['boundary_layer_heat_fluxes']
            # finds temperature values at the closest model height to obs
            modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                               heightindexlon]

            # taking the next closest heights
            modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                heightindexlon0]
            modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                                heightindexlon2]


        elif variable == 'LE':

            if MO_format == 'old':
                modtemplon = modlon_ncfile.variables['bl_mf']
                modtempvalueslon = modtemplon[0, index_to_start:, 0, 1, 1]

                # taking the next closest heights
                modtempvalueslon0 = modtemplon[0, index_to_start:, 0, 1, 1]
                modtempvalueslon2 = modtemplon[0, index_to_start:, 0, 1, 1]

            elif MO_format == 'new':
                try:
                    modtemplon = modlon_ncfile.variables['surface_upward_latent_heat_flux']
                except:
                    modtemplon = modlon_ncfile.variables['surface_latent_heat_flux']
                modtempvalueslon = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
                # taking the next closest heights
                modtempvalueslon0 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
                modtempvalueslon2 = modtemplon[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]


            else:
                print('MO_format not an option.')
                sys.exit()



        else:
            print('variable choice not an option')
            sys.exit()

        # append times to a list to plot outside of the for loop
        for timevalue in modtimeslon:
            lontimedict[time].append(timevalue)
        # append temps to a list to plot outside of the for loop
        for value in modtempvalueslon:
            lontempdict[temp].append(value)

        # 3x3 grid average
        if MO_format == 'old':
            shape_number = 1
        elif MO_format == 'new':
            shape_number = 2
        else:
            print('MO_format is not an option.')
            sys.exit()

        for i in range(index_to_start, np.shape(modtemplon)[shape_number]):
            if variable == 'Tair':
                if MO_format == 'old':
                    modtempvalueslonmean = np.mean(modtemplon[0, i, heightindexlon, :, :] - 273.15)
                elif MO_format == 'new':
                    modtempvalueslonmean = np.mean(modtemplon[:, :, i, heightindexlon] - 273.15)
                else:
                    'MO_format is not an option.'
                    sys.exit()

            elif variable == 'RH':
                if MO_format == 'old':
                    modtempvalueslonmean = np.mean(modtemplon[0, i, heightindexlon, :, :])
                elif MO_format == 'new':
                    modtempvalueslonmean = np.mean(modtemplon[:, :, i, heightindexlon])
                else:
                    print('MO_format not an option.')
                    sys.exit()

            elif variable == 'BL_H':
                modtempvalueslonmean = np.mean(modtemplon[:, :, i, heightindexlon])

            elif variable == 'Press':
                if MO_format == 'old':
                    modtempvalueslonmean = np.mean(modtemplon[0, i, heightindexlon, :, :]) / 100.
                elif MO_format == 'new':
                    modtempvalueslonmean = np.mean(modtemplon[:, :, i, heightindexlon]) / 100.
                else:
                    print('MO_format not an option.')
                    sys.exit()

            elif variable == 'kdown' or variable == 'kup' or variable == 'ldown' or variable == 'lup':
                if MO_format == 'old':
                    modtempvalueslonmean = np.mean(modtemplon[0, i, :, :])
                elif MO_format == 'new':
                    modtempvalueslonmean = np.mean(modtemplon[:, :, i])
                else:
                    print('MO_format not an option.')
                    sys.exit()

            elif variable == 'netallwave':

                ldown_mean = np.mean(ldown[0, i, :, :])
                lup_mean = np.mean(lup[0, i, :, :])
                kup_mean = np.mean(kup[0, i, :, :])
                kdown_mean = np.mean(kdown[0, i, :, :])

                modtempvalueslonmean = ldown_mean - lup_mean + kdown_mean - kup_mean

            elif variable == 'H' or variable == 'LE':
                if MO_format == 'old':
                    modtempvalueslonmean = np.mean(modtemplon[0, i, 0, :, :])
                elif MO_format == 'new':
                    modtempvalueslonmean = np.mean(modtemplon[:, :, i])
                else:
                    print('MO_format not an option.')
                    sys.exit()


            else:
                print('variable choice not an option.')
                sys.exit()

            # append temps9 to a list to plot outside of the for loop
            lontempdict9[temp9].append(modtempvalueslonmean)

        # fromliam: [np.mean(modtemplon[0,i,heightindexlon,:,:] -273.15) for i in range(37)]

        # taking the next closest heights
        for item0 in modtempvalueslon0:
            lontempdict0[temp0].append(item0)
        for item2 in modtempvalueslon2:
            lontempdict2[temp2].append(item2)

    # print out any dodgey model files with huge time array lengths...
    print('number of dodgey model files:', len(dodgeyfileslon))
    if len(dodgeyfileslon) == 0:
        pass
    else:
        print(dodgeyfileslon)

    # deletes placeholder
    for item in lontempdict:
        if lontempdict[item][0] == 'placeholder':
            del lontempdict[item][0]
    for item in lontimedict:
        if lontimedict[item][0] == 'placeholder':
            del lontimedict[item][0]
    for item in lontempdict9:
        if lontempdict9[item][0] == 'placeholder':
            del lontempdict9[item][0]
    for item in lontempdict0:
        if lontempdict0[item][0] == 'placeholder':
            del lontempdict0[item][0]
    for item in lontempdict2:
        if lontempdict2[item][0] == 'placeholder':
            del lontempdict2[item][0]

    # names to use for plotting in order - otherwise strange lines appear all over the plot,
    # trying to link datetimes together
    stringtemplon = []
    for item in sorted(lontempdict):
        stringtemplon.append(item)
    stringtimelon = []
    for item in sorted(lontimedict):
        stringtimelon.append(item)
    stringtemplon9 = []
    for item in sorted(lontempdict9):
        stringtemplon9.append(item)
    # heights 0 and 2
    stringtemplon0 = []
    for item in sorted(lontempdict0):
        stringtemplon0.append(item)
    stringtemplon2 = []
    for item in sorted(lontempdict2):
        stringtemplon2.append(item)

    # A test to see if there are any repeated times within the London model,
    # as part of the 'strange lines on plot' debugging
    alllontimes = []
    for item in stringtimelon:
        for time in lontimedict[item][:hoursbeforerepeat]:
            alllontimes.append(time)
    print(' ')
    print('Finding any dupulate times:')
    if len(set([x for x in alllontimes if alllontimes.count(x) > 1])) == 0:
        print('No duplicates')
    else:
        print(len(set([x for x in alllontimes if alllontimes.count(x) > 1])), 'Duplicates')
        repeats = list(set([x for x in alllontimes if alllontimes.count(x) > 1]))
        print(repeats)

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
    # ToDo: should I be included the height above and below here?
    for temp, tempall, time in zip(stringtemplon,
                                   stringtemplon9,
                                   stringtimelon
                                   ):

        if len(lontimedict[time][:hoursbeforerepeat]) == 0:
            print('There was a time list which has length 0: ', time)

            stringtemplon.remove(temp)
            stringtemplon9.remove(tempall)
            stringtimelon.remove(time)

            # not sure I need these:
            del lontimedict[time]
            del lontempdict[temp]
            del lontempdict9[tempall]

    # plotting the differences between 3x3 averaged and centre grid
    plt.figure(figsize=(20, 10))
    ax = pyplot.subplot(1, 1, 1)

    mod_colour = look_up.model_options[model][1]

    # for temp, time in zip(stringtemplon9, stringtimelon):
    #     plotCollection(ax, lontimedict[time][:hoursbeforerepeat], lontempdict9[temp][:hoursbeforerepeat], 'g',
    #                    label="3x3 averaged %s @ %d m" % (model, modheightvaluelon))

    for temp, time in zip(stringtemplon, stringtimelon):
        # plotCollection calling the function that sorts out repeated
        # labels in the legend, defined in the observations section
        plotting_funs.plotCollection(ax, lontimedict[time][:], lontempdict[temp][:], mod_colour,
                                     label="%s @ %d m" % (model, modheightvaluelon))

    plt.xlabel('DOY')
    plt.ylabel(label_string)
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_formatter(DateFormatter('%j'))

    date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
    plt.title(sitechoice + ': ' + date_for_title)

    if saveyn == 0:
        plt.show()
    if saveyn == 1:
        pylab.savefig(savestring + str(variable) + '_' + str(model) + '_' + sitechoice + '_' +
                      str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')

    return (lontimedict,
            lontempdict,
            lontempdict9,
            lontempdict0,
            lontempdict2,
            stringtimelon,
            stringtemplon,
            stringtemplon9,
            stringtemplon0,
            stringtemplon2,
            modheightvaluelon,
            modheightvaluelon0,
            modheightvaluelon2,
            alllontimes)
