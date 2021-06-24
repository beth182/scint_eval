# imports
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pylab
import numpy as np

from scint_eval import look_up


# function to group labels in the plots -- otherwise, the same label will appear multiple times
# as it gives one to each file/day being looped over
def plotCollection(ax, xs, ys, *args, **kwargs):
    ax.plot(xs, ys, *args, **kwargs)
    if "label" in kwargs.keys():
        # remove duplicates
        handles, labels = plt.gca().get_legend_handles_labels()
        newLabels, newHandles = [], []
        for handle, label in zip(handles, labels):
            if label not in newLabels:
                newLabels.append(label)
                newHandles.append(handle)
        # pyplot.legend(newHandles, newLabels, loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=12)
        plt.legend(newHandles, newLabels, bbox_to_anchor=(1, 0.5), fontsize=15, loc='center left')


# def time_series_hour(obs_time, obs, variable, included_models, DOYstart, DOYstop, saveyn, savestring):
#     """
#     Time series plot with only values on the hour
#     :return:
#     """
#
#     plt.figure(figsize=(20, 10))
#     ax = plt.subplot(1, 1, 1)
#
#     # Number of data points
#     # OBS
#     obs_N = sum(obs_time)
#
#     # choices dependent on variable choice
#     label_string = look_up.variable_info[variable][0]
#
#     # define a list of all included models
#     included_model_list = included_models.keys()
#     # define a dict to append features of included models to
#     new_model_dict = {}
#     # populates the new dict with keys
#     for model in included_model_list:
#         new_model_dict[model] = []
#     for model in included_model_list:
#         stringtempmodel = included_models[model][1]
#         modeltempdict = included_models[model][3]
#         model_N_list = []
#         for item in stringtempmodel:
#             model_N_list.append(len(modeltempdict[item][:]))
#         model_N = sum(model_N_list)
#         new_model_dict[model].append(model_N)
#
#     # plotting models
#     for model in included_model_list:
#
#         # seeing what the legend entry should be for this model - different for model level stashes or @ surface
#         modheightvaluemodel = included_models[model][4]
#         model_N = new_model_dict[model][0]
#
#         if look_up.variable_info[variable][1] == 'levels':
#             label_string_legend_model = str(model) + " @ %d m \n N = %d" % (modheightvaluemodel, model_N)
#
#         elif look_up.variable_info[variable][1] == 'surface':
#             label_string_legend_model = str(model) + " @ surface \n N = %d" % model_N
#
#         # appending legend entry in list
#         new_model_dict[model].append(label_string_legend_model)
#
#     # working out how many days I am working with - to make choices about how the plot is formatted
#     DOYchoices = []
#     for item in range(DOYstart, DOYstop + 1):
#         DOYchoices.append(item)
#
#     # colours for grid list choice
#     amout_of_grids = len(included_model_list)
#     c = np.arange(1, amout_of_grids + 1)
#     norm = mpl.colors.Normalize(vmin=c.min(), vmax=c.max())
#     cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.jet)
#     cmap.set_array([])
#
#     for i, model in enumerate(included_model_list):
#         stringtimemodel = included_models[model][0]
#         stringtempmodel = included_models[model][1]
#         modeltimedict = included_models[model][2]
#         modeltempdict = included_models[model][3]
#
#         for temp, time in zip(stringtempmodel, stringtimemodel):
#             colour_model = look_up.grid_dict_colours[model]
#             # colour_model = cmap.to_rgba(i + 1)
#
#             plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
#                            color=colour_model,
#                            label=new_model_dict[model][1])
#
#     # Plotting the Average and WAverage over the top
#     stringtimemodel = included_models['Average'][0]
#     stringtempmodel = included_models['Average'][1]
#     modeltimedict = included_models['Average'][2]
#     modeltempdict = included_models['Average'][3]
#
#     for temp, time in zip(stringtempmodel, stringtimemodel):
#         colour_model = look_up.grid_dict_colours['Average']
#         # colour_model = cmap.to_rgba(i + 1)
#
#         plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
#                        color=colour_model,
#                        label=new_model_dict['Average'][1])
#
#     stringtimemodel = included_models['WAverage'][0]
#     stringtempmodel = included_models['WAverage'][1]
#     modeltimedict = included_models['WAverage'][2]
#     modeltempdict = included_models['WAverage'][3]
#
#     for temp, time in zip(stringtempmodel, stringtimemodel):
#         colour_model = look_up.grid_dict_colours['WAverage']
#         # colour_model = cmap.to_rgba(i + 1)
#
#         plotCollection(ax, modeltimedict[time][:], modeltempdict[temp][:],
#                        color=colour_model,
#                        label=new_model_dict['WAverage'][1])
#
#     # Plotting observations
#
#     for temp, time in zip(stringtemp, stringtime):
#         plotCollection(ax, obvstimedict[time], obvstempdict[temp], color='k', linestyle='None',
#                        marker='.',
#                        label="Obs @ %d m \n N = %d" % (adjustedobvsheight, obs_N))
#
#     plt.ylabel(label_string)
#     plt.gcf().autofmt_xdate()
#
#     # setting the x-axis. DOY if more than 3 days, hour if less than 3 days
#     if len(DOYchoices) > 3:
#         ax.xaxis.set_major_formatter(DateFormatter('%j'))
#         plt.xlabel('DOY')
#         date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
#
#     else:
#
#         # if len(stringtime) == 2:
#         #     ax.set_xlim(obvstimedict[stringtime[0]][0], obvstimedict[stringtime[-1]][-1])
#
#         ax.xaxis.set_major_formatter(DateFormatter('%j %H:%M'))
#         plt.xlabel('Time')
#         date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
#
#     # plt.title(str(sitechoice) + ': ' + date_for_title)
#     plt.title(date_for_title)
#     # ax.get_legend().remove()
#
#     if saveyn == 0:
#         plt.show()
#     if saveyn == 1:
#         pylab.savefig(
#             savestring + str(variable) + '_lon_and_ukv_' + str(sitechoice) + '_' + str(
#                 DOYstart) + '_' + str(DOYstop) + '.png',
#             bbox_inches='tight')
