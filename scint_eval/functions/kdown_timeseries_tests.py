# imports
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pylab
import sys
import numpy as np
import datetime as dt

from scint_eval import look_up
from scint_eval.functions import tools
from scint_eval.functions import plotting_funs

def kdown_timeseries(obs_time, obs_vals,
                     obs_time_par, obs_vals_par,
                     mod_time, mod_vals,
                     sitechoice,
                     DOYstart, DOYstop, saveyn, savestring, variable):
    """
    Written to look at why modelled kdown looks different to observed (delay)
    :return:
    """

    time_0 = mod_time[0]

    epsunrise = tools.calculate_time(time_0, look_up.site_location[sitechoice][1],
                                     look_up.site_location[sitechoice][0],
                                     0, 0)
    epsunset = tools.calculate_time(time_0, look_up.site_location[sitechoice][1],
                                    look_up.site_location[sitechoice][0], 1,
                                    0)

    epnoon = tools.calculate_time(time_0, look_up.site_location[sitechoice][1],
                                  look_up.site_location[sitechoice][0], 2,
                                  0)

    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()

    ax.plot([epsunrise, epsunrise], [0, 700], color='orange', linestyle='--', lw=2,
             label='sunrise')
    ax.plot([epsunset, epsunset], [0, 700], color='purple', linestyle='--', lw=2, label='sunset')
    ax.plot([epnoon, epnoon], [0, 900], color='red', linestyle='--', lw=2, label='noon')

    ax2.scatter(obs_time_par, obs_vals_par, color='green', label='PAR obs', marker='.')

    ax.scatter(obs_time, obs_vals, marker='.', color='k', label='kdn obs')
    ax.plot(mod_time, mod_vals, color='blue', label='kdn mod')

    index_max_ob = np.where(obs_vals == np.max(obs_vals))[0]
    index_max_mod = np.where(mod_vals == np.max(mod_vals))[0]
    index_max_ob_par = np.where(obs_vals_par == np.max(obs_vals_par))[0]

    ax.scatter(obs_time[index_max_ob], obs_vals[index_max_ob], color='r', marker='o')
    ax2.scatter(obs_time_par[index_max_ob_par], obs_vals_par[index_max_ob_par], color='r', marker='o')
    ax.scatter(mod_time[index_max_mod], mod_vals[index_max_mod], color='r', marker='o')

    label_string = look_up.variable_info[variable][0]

    ax.set_ylabel(label_string)
    ax2.set_ylabel('PAR W m$^{-2}$')
    plt.gcf().autofmt_xdate()

    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)

    # working out how many days I am working with - to make choices about how the plot is formatted
    DOYchoices = []
    for item in range(DOYstart, DOYstop + 1):
        DOYchoices.append(item)

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
        pylab.savefig(
            savestring + str(variable) + '_lon_and_ukv_' + str(sitechoice) + '_' + str(DOYstart) + '_' + str(
                DOYstop) + '.png', bbox_inches='tight')

    print('end')

