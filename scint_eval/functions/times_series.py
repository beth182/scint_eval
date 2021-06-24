import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pylab
import sys
import numpy as np

from scint_eval import look_up
from scint_eval.functions import tools
from scint_eval.functions import plotting_funs

mpl.rcParams.update({'font.size': 20})  # updating the matplotlib fontsize


def time_series_plot(variable,
                     saveyn,
                     sitechoice,
                     DOYstart,
                     DOYstop,
                     savestring,
                     run,

                     included_models,

                     included_obs,

                     is_it_daily=False,

                     hoursbeforerepeat=24):
    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Model and obs plot')
    print(' ')

    # unpacking the grouped observations
    allobsarenans = included_obs[0]
    stringtime = included_obs[1]
    stringtemp = included_obs[2]
    obvstimedict = included_obs[3]
    obvstempdict = included_obs[4]
    adjustedobvsheight = included_obs[5]

    # Number of data points
    # OBS
    obs_N_list = []
    for item in stringtemp:
        obs_N_list.append(len(obvstempdict[item]))
    obs_N = sum(obs_N_list)

    # MODELS

    # define a list of all included models
    included_model_list = included_models.keys()

    # define a dict to append features of included models to
    new_model_dict = {}

    # populates the new dict with keys
    for model in included_model_list:
        new_model_dict[model] = []

    for model in included_model_list:

        stringtempmodel = included_models[model][1]
        modeltempdict = included_models[model][3]

        model_N_list = []
        for item in stringtempmodel:
            model_N_list.append(len(modeltempdict[item][:]))

        model_N = sum(model_N_list)

        new_model_dict[model].append(model_N)

    # plotting

    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    plt.figure(figsize=(20, 10))
    ax = plt.subplot(1, 1, 1)

    # if there is no obs or model data
    if len(obvstimedict) == 0 and len(included_models) == 0:
        plt.text(0.5, 0.5, 'Observation and model data \n are missing!',
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax.transAxes,
                 fontsize=22)
        if saveyn == 0:
            plt.show()
        if saveyn == 1:

            # are we runnign the daily plots?
            # if we are, this affects where we should save these files
            if is_it_daily == False:
                pylab.savefig(
                    savestring + str(variable) + '_lon_and_ukv_' + str(sitechoice) + '_' + str(
                        DOYstart) + '_' + str(DOYstop) + '.png',
                    bbox_inches='tight')
            else:
                # it is a daily run
                pylab.savefig('/storage/basic/micromet/Tier_processing//rv006011/gluster_replacement/' +
                              str(sitechoice) + '_' + str(DOYstart) + '_' + variable + '.png',
                              bbox_inches='tight')

                pylab.savefig(
                    '/storage/silver/metweb/new-web/micromet/scripts/plots/ModEval/ModEval_' + variable + '_' + str(
                        sitechoice) + '.png',
                    bbox_inches='tight')

    # if there are no model data and all the obs data are nans
    elif len(included_models) == 0 and allobsarenans == True:
        plt.text(0.5, 0.5, 'Observation and model data \n are missing!',
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax.transAxes,
                 fontsize=22)
        if saveyn == 0:
            plt.show()
        if saveyn == 1:
            if is_it_daily == False:
                pylab.savefig(
                    savestring + str(variable) + '_lon_and_ukv_' + str(sitechoice) + '_' + str(
                        DOYstart) + '_' + str(DOYstop) + '.png',
                    bbox_inches='tight')
            else:
                # it is a daily run
                pylab.savefig('/storage/basic/micromet/Tier_processing/rv006011/gluster_replacement/' +
                              str(sitechoice) + '_' + str(DOYstart) + '_' + variable + '.png',
                              bbox_inches='tight')

                pylab.savefig(
                    '/storage/silver/metweb/new-web/micromet/scripts/plots/ModEval/ModEval_' + variable + '_' + str(
                        sitechoice) + '.png',
                    bbox_inches='tight')

    # if there are model data OR observation data OR both sets of data
    else:

        # working out how many days I am working with - to make choices about how the plot is formatted
        DOYchoices = []
        for item in range(DOYstart, DOYstop + 1):
            DOYchoices.append(item)

        if run == '06Z':
            # if there is only one DOY, and the model is 06Z, forces start at midnight
            if len(DOYchoices) == 1:

                for model in included_model_list:
                    stringtimemodel = included_models[model][0]
                    stringtempmodel = included_models[model][1]
                    modeltimedict = included_models[model][2]
                    modeltempdict = included_models[model][3]

                if len(stringtimemodel) == 2:
                    modeltimedict[stringtimemodel[0]] = modeltimedict[stringtimemodel[0]][15:hoursbeforerepeat]
                    modeltempdict[stringtempmodel[0]] = modeltempdict[stringtempmodel[0]][15:hoursbeforerepeat]

        elif run == '21Z':
            # hoursbeforerepeat += 1
            pass
        else:
            print('run choice not an option.')
            sys.exit()

        # plotting models
        for model in included_model_list:

            # seeing what the legend entry should be for this model - different for model level stashes or @ surface
            modheightvaluemodel = included_models[model][4]
            model_N = new_model_dict[model][0]

            if look_up.variable_info[variable][1] == 'levels':
                label_string_legend_model = str(model) + " @ %d m \n N = %d" % (modheightvaluemodel, model_N)

            elif look_up.variable_info[variable][1] == 'surface':
                label_string_legend_model = str(model) + " @ surface \n N = %d" % model_N

            # appending legend entry in list
            new_model_dict[model].append(label_string_legend_model)

        if type(sitechoice) == str:
            pass
        else:
            # colours for grid list choice
            amout_of_grids = len(included_model_list)
            c = np.arange(1, amout_of_grids + 1)
            norm = mpl.colors.Normalize(vmin=c.min(), vmax=c.max())
            cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.jet)
            cmap.set_array([])

        for i, model in enumerate(included_model_list):
            stringtimemodel = included_models[model][0]
            stringtempmodel = included_models[model][1]
            modeltimedict = included_models[model][2]
            modeltempdict = included_models[model][3]

            # if its a string for a site
            if type(sitechoice) == str:
                for temp, time in zip(stringtempmodel, stringtimemodel):

                    # adds the sunrise sunset line
                    if variable == 'kdown':
                        time_0 = modeltimedict[time][:][0]

                        epsunrise = tools.calculate_time(time_0, look_up.site_location[sitechoice][1],
                                                         look_up.site_location[sitechoice][0],
                                                         0, 0)
                        epsunset = tools.calculate_time(time_0, look_up.site_location[sitechoice][1],
                                                        look_up.site_location[sitechoice][0], 1,
                                                        0)

                        plt.plot([epsunrise, epsunrise], [0, 700], color='orange', linestyle='--', lw=2,
                                 label='sunrise')
                        plt.plot([epsunset, epsunset], [0, 700], color='purple', linestyle='--', lw=2, label='sunset')

                    else:
                        pass

                    plotting_funs.plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
                                                 color=look_up.model_options[model][1],
                                                 label=new_model_dict[model][1])


            else:

                for temp, time in zip(stringtempmodel, stringtimemodel):
                    colour_model = look_up.grid_dict_colours[model]
                    # colour_model = cmap.to_rgba(i + 1)

                    plotting_funs.plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
                                                 color=colour_model,
                                                 label=new_model_dict[model][1])

        # Plotting the Average and WAverage over the top

        if type(sitechoice) == str:
            pass
        else:

            stringtimemodel = included_models['Average'][0]
            stringtempmodel = included_models['Average'][1]
            modeltimedict = included_models['Average'][2]
            modeltempdict = included_models['Average'][3]

            for temp, time in zip(stringtempmodel, stringtimemodel):
                colour_model = look_up.grid_dict_colours['Average']
                # colour_model = cmap.to_rgba(i + 1)

                plotting_funs.plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
                                             color=colour_model,
                                             label=new_model_dict['Average'][1])

            stringtimemodel = included_models['WAverage'][0]
            stringtempmodel = included_models['WAverage'][1]
            modeltimedict = included_models['WAverage'][2]
            modeltempdict = included_models['WAverage'][3]

            for temp, time in zip(stringtempmodel, stringtimemodel):
                colour_model = look_up.grid_dict_colours['WAverage']
                # colour_model = cmap.to_rgba(i + 1)

                plotting_funs.plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
                                             color=colour_model,
                                             label=new_model_dict['WAverage'][1])

        # Plotting observations
        if allobsarenans == True:
            print("All obs are nans; can't plot the obs")
        else:

            for temp, time in zip(stringtemp, stringtime):
                plotting_funs.plotCollection(ax, obvstimedict[time], obvstempdict[temp], color='k', linestyle='None',
                                             marker='.',
                                             label="Obs @ %d m \n N = %d" % (adjustedobvsheight, obs_N))

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

        # plt.title(str(sitechoice) + ': ' + date_for_title)
        plt.title(date_for_title)
        # ax.get_legend().remove()

        if saveyn == 0:
            plt.show()
        if saveyn == 1:
            if is_it_daily == False:
                pylab.savefig(
                    savestring + str(variable) + '_lon_and_ukv_' + str(sitechoice) + '_' + str(
                        DOYstart) + '_' + str(DOYstop) + '.png',
                    bbox_inches='tight')
            else:
                # it is a daily run
                pylab.savefig('/storage/basic/micromet/Tier_processing/rv006011/gluster_replacement/' +
                              str(sitechoice) + '_' + str(DOYstart) + '_' + variable + '.png',
                              bbox_inches='tight')

                pylab.savefig(
                    '/storage/silver/metweb/new-web/micromet/scripts/plots/ModEval/ModEval_' + variable + '_' + str(
                        sitechoice) + '.png',
                    bbox_inches='tight')
