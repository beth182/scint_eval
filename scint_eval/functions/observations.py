# imports
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import netCDF4 as nc
import pylab
from matplotlib import pyplot
import sys
import numpy as np

from scint_eval import look_up
from scint_eval.functions import plotting_funs

mpl.rcParams.update({'font.size': 20})  # updating the matplotlib fontsize


# ----------------------------------------------------------------------------------------------------------------------
def sort_obs(variable,
             files,
             DOYstart,
             DOYstop,
             sitechoice,
             z0zd,
             saveyn,
             savestring,
             sample,
             instrument):
    """
    Sorts observations, and produces a time series plot of the obs for a variable, from 1 site.

    :param variable: choice of variable. Entered as a string.
    Can so far be: 'Tair' or 'wind' or 'RH'
    :param files: From finding_files: 3 dictionaries of filepaths of data to be read in. Observations, London model
    and the ukv. Originally from the functions findfiles (for the cluster), and findfilesold (for laptop/desktop).
    :param DOYstart: date choices, where DOY is day of year. Start of date range.
    This is to be entered as a normal number, i.e. do not wrap
    one didget DOYs with 0's (example: DOY one is 1, and not 001).
    :param DOYstop: date choices, where DOY is day of year. End of date range. (Also, see above for DOYstart format).
    :param sitechoice: Choice of site.
    This is entered as a string.
    :param z0zd: List of different roughness lengths and displacement heights for the models and observations.
    This is output from the function roughness_and_displacement.
    In the order of: [z01 (z0 for the 1-tile), z0m (z0 for MORUSES), z0o (z0 for observations),
    zdo (zd for observations), z0do (the combination of z0o and zdo)].
    :param saveyn: decides whether to save a plot made, or show it.
    1 = save, 0 = show
    :param savestring: Where to save the plots produced.


    :return obvstimedict: Dictionary of lists of time values for each file.
    :return obvstempdict or obvswinddict or obvsdirdict: Dictionary of lists of values for each file.
    :return stringtime: List of strings of keys in the obvstimedict, to call in order when plotting.
    :return stringtemp or stringwind or stringdir: List of strings of keys in the obvstempdict,
    to call in order when plotting.
    :return allobvsarenans: Tells me if all the observations of the chosen rime range are all NaNs or not.
    In the form of True or False.
    :return adjustedobvsheight: Height of observation, MASL.
    :return disheight: Height of observation, adjusting for roughness length and displacement height.
    :return lat: latitude of the obs site
    :return longitude: longitude of the obs site
    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Sorting observations')
    print(' ')

    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    # working out how many days I am working with - to make choices about how the plot is formatted
    DOYchoices = []
    for item in range(DOYstart, DOYstop + 1):
        DOYchoices.append(item)

    if len(files) == 0:
        print('There are no observations!')

        if variable == 'wind' or variable == 'kup':
            obvstimedict = []
            obvstempdict = []
            obvsdirdict = []
            stringtime = []
            stringtemp = []
            stringwind = []
            stringdir = []
            allobvsarenans = []
            obvheightvalue = []
            disheight = []
            lat = []
            lon = []

            return (obvstimedict,
                    obvstempdict,
                    obvsdirdict,
                    stringtime,
                    stringtemp,
                    stringwind,
                    stringdir,
                    allobvsarenans,
                    obvheightvalue,  # used to be adjustedobvsheight 27/3/18
                    disheight,
                    lat,
                    lon)

        else:
            obvstimedict = []
            obvstempdict = []
            stringtime = []
            stringtemp = []
            allobvsarenans = []
            obvheightvalue = []
            disheight = []
            lat = []
            lon = []

            return (obvstimedict,
                    obvstempdict,
                    stringtime,
                    stringtemp,
                    allobvsarenans,
                    obvheightvalue,  # used to be adjustedobvsheight 27/3/18
                    disheight,
                    lat,
                    lon)

    # ----------------------------------------------------
    # The following depends on the variable choice.
    # Wind behaves differently to other variables, as it involves both speed and direction.
    if variable == 'wind' or variable == 'kup':
        # creates lists to plot outside of the for loop
        obvstimedict = {}
        for item in files.keys():
            varname = "time" + str(item)
            obvstimedict[varname] = []
            # temporarily adds 'placeholder' as the first item of each list, to get python to reckognise
            # that there is actually a list there
            obvstimedict[varname].append('placeholder')
        # wind
        obvswinddict = {}
        for item in files.keys():
            varname = "wind" + str(item)
            obvswinddict[varname] = []
            obvswinddict[varname].append('placeholder')
        # dir
        obvsdirdict = {}
        for item in files.keys():
            varname = "dir" + str(item)
            obvsdirdict[varname] = []
            obvsdirdict[varname].append('placeholder')

        # loops over the observation file paths in obvsdict (to import the data each time), and the empty lists ready in
        # obvswinddict, obvsdirdict and obvstimedict - these will be dictionries including lists full of wind speeds,
        # wind direction
        # and time respectively. One list for each day/ file in the observation files
        for item, wind, time, direction in zip(sorted(files.values()), sorted(obvswinddict), sorted(obvstimedict),
                                               sorted(obvsdirdict)):
            # assigns observation .nc file
            obvspath = item
            obvs_ncfile = nc.Dataset(obvspath)
            # reads in observation height
            obvheight = obvs_ncfile.variables['height']
            obvheightvalue = obvheight[:]
            # reads in obvs time
            obvstime = obvs_ncfile.variables['time']
            # converts to datetime
            obvstime_dt = nc.num2date(obvstime[:], obvstime.units)

            if variable == 'wind':
                # reads in obvs wind speed
                obvswind = obvs_ncfile.variables['WS']
                obvswindvalues = obvswind[:, 0, 0, 0]
                # reads in obvs wind direction
                obvsdir = obvs_ncfile.variables['dir']
                obvsdirvalues = obvsdir[:, 0, 0, 0]

            elif variable == 'kup':

                # DOWN AS U, AND STAR AS V
                # WIND AS UP, AND STAR AS DIR

                obvswind = obvs_ncfile.variables['Kup']

                obvswindvalues = obvswind[:, 0, 0, 0]
                # reads in obvs wind direction
                obvsdir = obvs_ncfile.variables['Kup']
                obvsdirvalues = obvsdir[:, 0, 0, 0]

            # append items to a list to plot outside of the for loop
            for item in obvswindvalues:
                obvswinddict[wind].append(item)

            for item in obvstime_dt:
                obvstimedict[time].append(item)

                # For old method of adjusting time-ending samples to be time-starting - doesn't need to be in:
                """

                # observations are time ending - so I'm pusing them back by the sample:
                # I am currently the time-ending observation time stamps and convert them to time starting  by pushing
                # them back the amount of minutes the sampe is. This seems like the wrong thing to do?

                sample_minutes = int(sample[:-3])   # takes the sample and converts it to a number in minutes
                                                    # (cuts off "mins" on the string)
                new_time_val =  item - dt.timedelta(minutes=sample_minutes)

                obvstimedict[time].append(new_time_val)

                """

            for item in obvsdirvalues:
                obvsdirdict[direction].append(item)

        # goes through and deletes the placeholder string initially appened to get python to reckognise a list
        for item in obvswinddict:
            if obvswinddict[item][0] == 'placeholder':
                del obvswinddict[item][0]

        for item in obvstimedict:
            if obvstimedict[item][0] == 'placeholder':
                del obvstimedict[item][0]

        for item in obvsdirdict:
            if obvsdirdict[item][0] == 'placeholder':
                del obvsdirdict[item][0]

        # adjusting the observation height to no longer be in MASL.
        # this uses a value found for the site within the 'lidar_grounddem_4m.asc' file
        # found at: '/data/its-tier2/micromet/data/MAPS/Footprint/DEM/lidar_grounddem_4m.asc'
        # ToDo: make this flexable for other sites!
        # 27/3/18 -- taken out, to make new adjustment with the model
        # adjustedobvsheight = obvheightvalue - 17.98
        # adjusting for roughness length and displacement height
        disheight = obvheightvalue - z0zd[4]
        # names to use for plotting in order - otherwise strange lines appear all over the plot
        # trying to link datetimes together
        stringwind = []
        for item in sorted(obvswinddict):
            stringwind.append(item)
        stringtime = []
        for item in sorted(obvstimedict):
            stringtime.append(item)
        stringdir = []
        for item in sorted(obvsdirdict):
            stringdir.append(item)

        obvlon = obvs_ncfile.variables['lon']
        lon = obvlon[0]
        obvlat = obvs_ncfile.variables['lat']
        lat = obvlat[0]

        # plotting the observations

        if variable == 'wind':
            # the try statement is there to allow the code not to break if every singe observation is NaN
            # ToDo: make this except less general...
            try:
                plt.figure(figsize=(20, 15))
                ax1 = pyplot.subplot(2, 1, 1)
                ax2 = pyplot.subplot(2, 1, 2)
                for wind, time, direction in zip(stringwind, stringtime, stringdir):
                    # calls the plot collection function, to group all labels of the same thing together
                    plotting_funs.plotCollection(ax1, obvstimedict[time], obvswinddict[wind],
                                                 linestyle='None', marker='.',
                                                 color='k')
                    plotting_funs.plotCollection(ax2, obvstimedict[time], obvsdirdict[direction],
                                                 linestyle='None', marker='.',
                                                 color='k',
                                                 label="Obs @ %d m" % obvheightvalue)

                ax1.set_ylabel(label_string[0])
                ax2.set_ylabel(label_string[1])
                plt.gcf().autofmt_xdate()

                # setting the x-axis. DOY if more than 3 days, hour if less than 3 days
                if len(DOYchoices) > 3:
                    ax2.xaxis.set_major_formatter(DateFormatter('%j'))
                    plt.xlabel('DOY')
                    date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)

                else:

                    # if len(stringtime) == 2:
                    #     ax.set_xlim(obvstimedict[stringtime[0]][0], obvstimedict[stringtime[-1]][-1])

                    ax2.xaxis.set_major_formatter(DateFormatter('%j %H:%M'))
                    plt.xlabel('Time')
                    date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)

                # ax.xaxis.set_major_formatter(DateFormatter('%j'))
                # date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
                ax1.set_title(sitechoice + ': ' + date_for_title)

                if saveyn == 0:
                    plt.show()
                if saveyn == 1:
                    pylab.savefig(
                        savestring + str(variable) + '_obvs_' + sitechoice + '_' +
                        str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')
                allobvsarenans = False
            except:
                print(' ')
                print('Cant produce plot: all observations are nans')
                allobvsarenans = True

        elif variable == 'kup':
            # the try statement is there to allow the code not to break if every singe observation is NaN
            # ToDo: make this except less general...
            try:
                plt.figure(figsize=(20, 10))
                ax = pyplot.subplot(1, 1, 1)

                for wind, time in zip(stringwind, stringtime):
                    # calls the plot collection function, to group all labels of the same thing together
                    plotting_funs.plotCollection(ax, obvstimedict[time], obvswinddict[wind], 'k',
                                                 label="Obs @ %d m" % obvheightvalue)  # used to be adjustedobvsheight 27/3/18

                plt.xlabel('DOY')
                plt.ylabel(label_string)
                plt.gcf().autofmt_xdate()
                ax.xaxis.set_major_formatter(DateFormatter('%j'))

                if saveyn == 0:
                    plt.show()
                if saveyn == 1:
                    pylab.savefig(
                        savestring + str(variable) + '_obvs_' + sitechoice + '_' +
                        str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')
                allobvsarenans = False
            except:
                print(' ')
                print('Cant produce plot: all observations are nans')
                allobvsarenans = True

        return (obvstimedict,
                obvswinddict,
                obvsdirdict,
                stringtime,
                stringwind,
                stringdir,
                allobvsarenans,
                obvheightvalue,  # used to be adjustedobvsheight 27/3/18
                disheight,
                lat,
                lon)

    # ----------------------------------------------------
    # Else: all other variables other than wind.
    else:
        # creates lists to plot outside of the for loop
        obvstimedict = {}
        for item in files.keys():
            varname = "time" + str(item)
            obvstimedict[varname] = []
            # temporarily adds 'placeholder' as the first item of each list, to get python to reckognise
            # that there is actually a list there
            obvstimedict[varname].append('placeholder')
        obvstempdict = {}
        for item in files.keys():
            varname = "temp" + str(item)
            obvstempdict[varname] = []
            obvstempdict[varname].append('placeholder')

        # loops over the observation file paths in obvsdict (to import the data each time), and the empty lists ready in
        # obvstempdict and obvstimedict - these will be dictionries including lists full of
        # temperatures and time respectively,
        # one list for each day/ file in the observation files
        for item, temp, time in zip(sorted(files.values()), sorted(obvstempdict), sorted(obvstimedict)):
            # assigns observation .nc file
            obvspath = item
            obvs_ncfile = nc.Dataset(obvspath)
            # reads in observation height
            obvheight = obvs_ncfile.variables['height']
            obvheightvalue = obvheight[:]
            # reads in obvs time
            obvstime = obvs_ncfile.variables['time']
            # converts to datetime
            obvstime_dt = nc.num2date(obvstime[:], obvstime.units)
            if variable == 'Tair':
                # reads in obvs air temperature
                obvstair = obvs_ncfile.variables['Tair']
            elif variable == 'RH' or variable == 'RH_q':
                # reads in relative humidity
                obvstair = obvs_ncfile.variables['RH']
            elif variable == 'Press':
                # reads in Press
                obvstair = obvs_ncfile.variables['press']
            elif variable == 'kdown':
                # reads in incoming shortwave radiation
                obvstair = obvs_ncfile.variables['Kdn']
            elif variable == 'kup':
                # reads in outgoing shortwave radiation
                obvstair = obvs_ncfile.variables['Kup']
            elif variable == 'ldown':
                # reads in outgoing shortwave radiation
                obvstair = obvs_ncfile.variables['Ldn']
            elif variable == 'lup':
                # reads in outgoing shortwave radiation
                obvstair = obvs_ncfile.variables['Lup']
            elif variable == 'netallwave':
                # reads in net all-wave radiation
                obvstair = obvs_ncfile.variables['Qstar']
            elif variable == 'H':

                # reads in sensible heat flux
                obvstair = obvs_ncfile.variables['Q_H']

            elif variable == 'LE':
                # reads in latent heat flux
                obvstair = obvs_ncfile.variables['Q_E']

            # added for scintillometry eval
            elif variable == 'CT2':
                obvstair = obvs_ncfile.variables['CT2']
            elif variable == 'X_c':
                obvstair = obvs_ncfile.variables['X_c']
            elif variable == 'Y_c':
                obvstair = obvs_ncfile.variables['Y_c']
            elif variable == 'sd_v':
                obvstair = obvs_ncfile.variables['sd_v']
            elif variable == 'L':
                obvstair = obvs_ncfile.variables['L']
            elif variable == 'ustar':
                obvstair = obvs_ncfile.variables['ustar']

            else:
                try:
                    obvstair = obvs_ncfile.variables[variable]
                except:
                    raise ValueError('Variable choice not an option')

            obvstairvalues = obvstair[:, 0, 0, 0]

            if variable == 'H':

                # if the data is from the scintillometers, make positive
                if instrument == 'BLS' or instrument == 'LASMkII_Fast':
                    # make positive
                    obvstairvalues = np.abs(obvstairvalues)

                    # Addition 3/1//19 - to get rid of really large values of QH in the scintillometry
                    for index, item in enumerate(obvstairvalues):
                        if item > 1000:
                            obvstairvalues[index] = np.nan

            # append items to a list to plot outside of the for loop
            for value in obvstairvalues:
                obvstempdict[temp].append(value)

            for timevalue in obvstime_dt:
                obvstimedict[time].append(timevalue)

                # For old method of adjusting time-ending samples to be time-starting - doesn't need to be in:
                """

                # observations are time ending - so I'm pusing them back by the sample:
                # I am currently the time-ending observation time stamps and convert them to time starting  by pushing
                # them back the amount of minutes the sampe is. This seems like the wrong thing to do?

                sample_minutes = int(sample[:-3])   # takes the sample and converts it to a number in minutes
                                                    # (cuts off "mins" on the string)
                new_time_val =  timevalue - dt.timedelta(minutes=sample_minutes)

                obvstimedict[time].append(new_time_val)

                """

        # goes through and deletes the placeholder string initially append to get python to recognise list
        for item in obvstempdict:
            if obvstempdict[item][0] == 'placeholder':
                del obvstempdict[item][0]
        for item in obvstimedict:
            if obvstimedict[item][0] == 'placeholder':
                del obvstimedict[item][0]

        # adjusting the observation height to no longer be in MASL.
        # this uses a value found for the site within the 'lidar_grounddem_4m.asc' file
        # found at: '/data/its-tier2/micromet/data/MAPS/Footprint/DEM/lidar_grounddem_4m.asc'
        # ToDo: make this flexable for other sites!
        # 27/3/18 -- taken out, to make new adjustment with the model
        # adjustedobvsheight = obvheightvalue - 17.98
        # adjusting for roughness length and displacement height
        disheight = obvheightvalue - z0zd[4]
        # names to use for plotting in order - otherwise strange lines appear all over the plot,
        # trying to link datetimes together
        stringtemp = []
        for item in sorted(obvstempdict):
            stringtemp.append(item)
        stringtime = []
        for item in sorted(obvstimedict):
            stringtime.append(item)

        obvlon = obvs_ncfile.variables['lon']
        lon = obvlon[0]
        obvlat = obvs_ncfile.variables['lat']
        lat = obvlat[0]

        # plotting the observations
        # the try statement is there to allow the code not to break if every singe observation is NaN
        # ToDo: make this except less general...

        try:
            plt.figure(figsize=(20, 10))
            ax = pyplot.subplot(1, 1, 1)
            for temp, time in zip(stringtemp, stringtime):
                # calls the plot collection function, to group all labels of the same thing together
                plotting_funs.plotCollection(ax, obvstimedict[time], obvstempdict[temp], 'k',
                                             # linestyle='None',
                                             marker='.',
                                             label="Obs @ %d m" % obvheightvalue)  # used to be adjustedobvsheight 27/3/18

            plt.xlabel('DOY')
            plt.ylabel(label_string)
            plt.gcf().autofmt_xdate()

            # setting the x-axis. DOY if more than 3 days, hour if less than 3 days
            if len(DOYchoices) > 3:
                ax.xaxis.set_major_formatter(DateFormatter('%j'))
                plt.xlabel('DOY')
                date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)

            else:

                # if len(stringtime) == 2:
                #     ax.set_xlim(obvstimedict[stringtime[0]][0], obvstimedict[stringtime[-1]][-1])

                ax.xaxis.set_major_formatter(DateFormatter('%j %H:%M'))
                plt.xlabel('Time')
                date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)

            # ax.xaxis.set_major_formatter(DateFormatter('%j'))
            # date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
            plt.title(sitechoice + ': ' + date_for_title)

            if saveyn == 0:
                plt.show()
            if saveyn == 1:
                pylab.savefig(
                    savestring + str(variable) + '_obvs_' + sitechoice + '_' +
                    str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')
            allobvsarenans = False
        except:
            print(' ')
            print('Cant produce plot: all observations are nans')
            allobvsarenans = True

        return (obvstimedict,
                obvstempdict,
                stringtime,
                stringtemp,
                allobvsarenans,
                obvheightvalue,  # used to be adjustedobvsheight 27/3/18
                disheight,
                lat,
                lon)

# ----------------------------------------------------------------------------------------------------------------------
