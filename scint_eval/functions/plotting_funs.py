# imports
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pylab
import numpy as np
import datetime
from matplotlib import gridspec
import pandas as pd

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


def simple_times_series(time, obs, model_av, model_wav, zeff, variable, DOYstart, DOYstop, savestring, sitechoice):
    """

    :return:
    """

    plt.figure(figsize=(20, 10))
    ax = plt.subplot(1, 1, 1)
    label_string = look_up.variable_info[variable][0]

    obs_N = len(obs)

    plt.plot(time, model_av, label='Average', color='red')
    plt.plot(time, model_wav, label='WAverage', color='blue')
    plt.plot(time, obs, color='black', linestyle='None', marker='.', label="Obs @ %d m \n N = %d" % (zeff, obs_N))

    plt.legend()

    plt.ylabel(label_string)

    ax.xaxis.set_major_formatter(DateFormatter('%j %H:%M'))
    plt.xlabel('Time')
    date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
    plt.title(date_for_title)

    plt.gcf().autofmt_xdate()

    pylab.savefig(
        savestring + str(variable) + '_mod_and_obs_' + str(sitechoice) + '_' + str(
            DOYstart) + '_' + str(DOYstop) + '.png',
        bbox_inches='tight')


def detailed_time_series(obs_time, obs_vals,
                         obs_time_hourly, obs_vals_hourly,
                         model_grid_time, model_grid_vals,
                         variable, zeff, savepath, DOYstart, DOYstop,
                         model_site_dict,
                         percentage_covered_by_model):
    """

    :return:
    """

    fig = plt.figure(figsize=(20, 15))

    spec = gridspec.GridSpec(ncols=1, nrows=2,
                             height_ratios=[3, 1])

    ax1 = fig.add_subplot(spec[0])
    ax2 = fig.add_subplot(spec[1])

    label_string = look_up.variable_info[variable][0]

    obs_N_hourly = len(obs_vals_hourly)
    obs_N = len(obs_vals)

    per_covered = list_calculated_sum(model_grid_time, percentage_covered_by_model)

    max_grid_vals, min_grid_vals, n_grids = variation_in_grids(model_grid_time, model_grid_vals, model_site_dict)

    ax1.fill_between(model_grid_time[list(model_grid_time.keys())[0]], max_grid_vals, min_grid_vals, color='pink',
                     alpha=0.4, label='Model grid range')

    ax1.plot(model_grid_time['Average'], model_grid_vals['Average'], label='Average', color='red', marker='.')
    ax1.plot(model_grid_time['WAverage'], model_grid_vals['WAverage'], label='WAverage', color='blue', marker='.')

    ax1.plot(obs_time, obs_vals, linestyle='None', marker='.', color='grey',
             label="Obs @ %d m \n N = %d" % (zeff, obs_N))
    ax1.plot(obs_time_hourly, obs_vals_hourly, linestyle='None', marker='o', color='k',
             label="Obs ending on hour, N = %d" % obs_N_hourly)

    ax1.set_ylabel(label_string)

    ax1.xaxis.set_major_formatter(DateFormatter('%H'))
    ax1.set_xlabel('Time (h)')

    # ax1.set_xlim([datetime.datetime(2016, 5, 21, 4, 30), datetime.datetime(2016, 5, 21, 19, 30)])

    plt.gcf().autofmt_xdate()

    date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
    ax1.set_title(date_for_title)

    ax1.legend(bbox_to_anchor=(1, 0.5), fontsize=15, loc='center left')

    ax2.plot(model_grid_time[list(model_grid_time.keys())[0]], n_grids, marker='x', linestyle='None', color='k')
    ax2.set_xlabel('Time (h)')
    ax2.xaxis.set_major_formatter(DateFormatter('%H'))
    ax2.set_ylabel("# of grids in source area")
    # ax2.set_xlim([datetime.datetime(2016, 5, 21, 4, 30), datetime.datetime(2016, 5, 21, 19, 30)])

    ax3 = ax2.twinx()
    # 50 because that is the max percentage currently coming out of the SA model repo for the example day
    ax3.plot(model_grid_time[list(model_grid_time.keys())[0]], (np.asarray(per_covered) / 100) * 50, marker='^',
             linestyle='None', color='green')
    ax3.set_ylabel("% SA covered by grid network")
    ax3.xaxis.set_major_formatter(DateFormatter('%H'))

    ax3.yaxis.label.set_color('green')
    ax3.tick_params(axis='y', colors='green')

    plt.tight_layout()

    plt.savefig(savepath + str(variable) + '_detail_time_series.png',
                bbox_inches='tight')

    # print('end')


def list_calculated_sum(model_grid_time, percentage_covered_by_model):
    """

    :return:
    """

    per_covered = []

    times_list = model_grid_time[list(model_grid_time.keys())[0]]

    for i, time in enumerate(times_list):

        time_string = time.strftime("%y%m%d%H")

        try:
            per_cover = percentage_covered_by_model[time_string]
        except KeyError:
            per_cover = np.nan

        per_covered.append(per_cover)

    return per_covered


def variation_in_grids(model_grid_time, model_grid_vals, model_site_dict):
    """
    Defines thickness of line in detailed time series by calculating the differences between model grids
    :return:
    """

    max_vals = []
    min_vals = []
    n_grids = []

    times_list = model_grid_time[list(model_grid_time.keys())[0]]

    for i, time in enumerate(times_list):

        time_string = time.strftime("%y%m%d%H")

        try:
            grid_list = model_site_dict[time_string]
        except KeyError:
            grid_list = []

        n_model_grids = len(grid_list)

        vals_list = []

        for grid_string in grid_list:
            grid = int(grid_string)

            val = model_grid_vals[grid][i]
            vals_list.append(val)

        if vals_list == []:
            max_val = np.nan
            min_val = np.nan
        else:
            max_val = max(vals_list)
            min_val = min(vals_list)

        max_vals.append(max_val)
        min_vals.append(min_val)

        n_grids.append(n_model_grids)

    return max_vals, min_vals, n_grids


def plots_vars(all_days_vars):
    """
    Makes stacked plot of retrieved vars
    :param all_days_vars:
    :return:
    """

    for day in sorted(all_days_vars.keys()):

        var_dict = all_days_vars[day]

        time = var_dict['time']
        QH = var_dict['QH']
        z_f = var_dict['z_f']
        wind_direction = var_dict['wind_direction']
        wind_speed = var_dict['wind_speed_adj']
        stab_param = var_dict['stab_param']


        df_dict = {'time': time, 'QH': QH, 'z_f': z_f, 'wind_direction': wind_direction, 'wind_speed': wind_speed, 'stab_param': stab_param}

        df = pd.DataFrame(df_dict)
        df = df.set_index('time')

        # average df
        five_min = df.resample('5T', closed='right', label='right').mean()
        fifteen_min = df.resample('15T', closed='right', label='right').mean()
        sixty_min = df.resample('60T', closed='right', label='right').mean()

        plt.figure(figsize=(10, 70))
        ax5 = plt.subplot(5, 1, 1)
        ax4 = plt.subplot(5, 1, 2)
        ax3 = plt.subplot(5, 1, 3)
        ax2 = plt.subplot(5, 1, 4)
        ax1 = plt.subplot(5, 1, 5)

        ax1.plot(df.index, df['z_f'], color='k')
        ax1.set_ylabel('z_f')

        # QH
        ax2.scatter(df.index, df['QH'], marker='.', label='1min', alpha=0.15, color='blue', s=10)
        ax2.scatter(five_min.index, five_min['QH'], marker='o', label='5min', alpha=0.4, color='blue', s=10)
        ax2.scatter(fifteen_min.index, fifteen_min['QH'], marker='^', label='15min', alpha=0.7, color='blue', s=20)
        ax2.scatter(sixty_min.index, sixty_min['QH'], marker='s', label='60min', alpha=1.0, color='blue', s=30)
        ax2.set_ylabel('QH')
        ax2.set_xticks([])
        ax2.legend()

        # STAB
        ax3.scatter(df.index, df['stab_param'], marker='.', label='1min', alpha=0.15, color='green', s=10)
        ax3.scatter(five_min.index, five_min['stab_param'], marker='o', label='5min', alpha=0.4, color='green', s=10)
        ax3.scatter(fifteen_min.index, fifteen_min['stab_param'], marker='^', label='15min', alpha=0.7, color='green', s=20)
        ax3.scatter(sixty_min.index, sixty_min['stab_param'], marker='s', label='60min', alpha=1.0, color='green', s=30)
        ax3.set_ylabel('z/L')
        ax3.set_xticks([])

        # WD
        ax4.scatter(df.index, df['wind_direction'], marker='.', label='1min', alpha=0.15, color='purple', s=10)
        ax4.scatter(five_min.index, five_min['wind_direction'], marker='o', label='5min', alpha=0.4, color='purple', s=10)
        ax4.scatter(fifteen_min.index, fifteen_min['wind_direction'], marker='^', label='15min', alpha=0.7, color='purple', s=20)
        ax4.scatter(sixty_min.index, sixty_min['wind_direction'], marker='s', label='60min', alpha=1.0, color='purple', s=30)
        ax4.set_ylabel('wind direction')
        ax4.set_xticks([])

        ax5.scatter(df.index, df['wind_speed'], marker='.', label='1min', alpha=0.15, color='red', s=10)
        ax5.scatter(five_min.index, five_min['wind_speed'], marker='o', label='5min', alpha=0.4, color='red', s=10)
        ax5.scatter(fifteen_min.index, fifteen_min['wind_speed'], marker='^', label='15min', alpha=0.7, color='red', s=20)
        ax5.scatter(sixty_min.index, sixty_min['wind_speed'], marker='s', label='60min', alpha=1.0, color='red', s=30)
        ax5.set_ylabel('wind speed')
        ax5.set_xticks([])

        plt.tight_layout()
        plt.subplots_adjust(wspace=0, hspace=0)

        plt.gcf().autofmt_xdate()
        ax1.xaxis.set_major_formatter(DateFormatter('%j %H'))
        ax1.set_xlabel('DOY HH')



        plt.show()


        print('end')



    print('end')