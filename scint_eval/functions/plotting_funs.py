# imports
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pylab
import numpy as np
import datetime
from matplotlib import gridspec
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.dates as mdates
import datetime as dt
from matplotlib import cm
import matplotlib as mpl
from scipy import stats

mpl.rcParams.update({'font.size': 15})

from scint_eval import look_up
from scint_fp.functions import wx_u_v_components
# from scint_eval.functions import read_ceda_heathrow


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
                         model_grid_time, model_grid_vals,
                         variable, savepath, DOYstart, DOYstop,
                         model_site_dict,
                         percentage_covered_by_model, BL_H_z=0):
    """

    :return:
    """

    fig = plt.figure(figsize=(15, 15))

    spec = gridspec.GridSpec(ncols=1, nrows=2,
                             height_ratios=[4, 1])

    mpl.rcParams.update({'font.size': 22})

    ax1 = fig.add_subplot(spec[0])
    ax2 = fig.add_subplot(spec[1])

    label_string = look_up.variable_info[variable][0]

    df_dict = {'time': obs_time, 'qh': obs_vals}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df.index = df.index.round('1s')

    five_min = df.resample('5T', closed='right', label='right').mean()
    ten_min = df.resample('10T', closed='right', label='right').mean()
    sixty_min = df.resample('60T', closed='right', label='right').mean()

    hour_1min = df.qh[np.where([i.minute == 0 for i in df.index])[0]]
    hour_5min = five_min.qh[np.where([i.minute == 0 for i in five_min.index])[0]]
    hour_10min = ten_min.qh[np.where([i.minute == 0 for i in ten_min.index])[0]]
    hour_60min = sixty_min.qh[np.where([i.minute == 0 for i in sixty_min.index])[0]]

    obs_N = len(df)

    # per_covered = list_calculated_sum(model_grid_time, percentage_covered_by_model)
    max_grid_vals, min_grid_vals, n_grids = variation_in_grids(model_grid_time, model_grid_vals, model_site_dict)
    ax1.fill_between(model_grid_time[list(model_grid_time.keys())[0]], max_grid_vals, min_grid_vals, color='pink',
                     alpha=0.8, label='Model grid range')
    # ax1.plot(model_grid_time['Average'], model_grid_vals['Average'], label='Average', color='red', marker='.')
    ax1.plot(model_grid_time['WAverage'], model_grid_vals['WAverage'], label='WAverage @ surface', color='blue',
             marker='.')

    first_index = np.where(model_grid_time[13] == model_grid_time['Average'][0])[0][0]
    last_index = np.where(model_grid_time[13] == model_grid_time['Average'][-1])[0][0] + 1
    ax1.plot(model_grid_time[13][first_index:last_index], model_grid_vals[13][first_index:last_index], label='13 @ surface', color='green',
             marker='.')

    # if I am including the BL_H grid
    try:
        first_index = np.where(model_grid_time['BL_H_13'] == model_grid_time['Average'][0])[0][0]
        last_index = np.where(model_grid_time['BL_H_13'] == model_grid_time['Average'][-1])[0][0] + 1
        ax1.plot(model_grid_time['BL_H_13'][first_index:last_index], model_grid_vals['BL_H_13'][first_index:last_index],
                 label='BL Flux @ ' + str(BL_H_z) + ' m', color='red', marker='.')
    except KeyError:
        pass

    ax1.plot(df.index, df['qh'], linestyle='None', marker='.', color='grey', alpha=0.5,
             label="1 min obs, N = %d" % obs_N)

    ax1.plot(hour_1min.index, hour_1min.values, linestyle='None', marker='o', color='k', markersize=8,
             label="1 min obs on hour")

    ax1.plot(hour_5min.index, hour_5min.values, linestyle='None', marker='o', color='green', markersize=8,
             label="5 min obs on hour")

    ax1.plot(hour_10min.index, hour_10min.values, linestyle='None', marker='^', color='red', markersize=8,
             label="10 min obs on hour")

    ax1.plot(hour_60min.index, hour_60min.values, linestyle='None', marker='x', color='purple', markersize=8,
             label="60 min obs")

    ax1.set_ylabel(label_string)

    ax1.xaxis.set_major_formatter(DateFormatter('%H'))
    ax1.set_xlabel('Time (h)')

    ax1.set_xlim([obs_time[0] - dt.timedelta(minutes=15), obs_time[-1] + dt.timedelta(minutes=15)])
    ax2.set_xlim([obs_time[0] - dt.timedelta(minutes=15), obs_time[-1] + dt.timedelta(minutes=15)])

    plt.gcf().autofmt_xdate()

    date_for_title = 'DOY ' + str(DOYstart)[-3:]
    # ax1.set_title(date_for_title)

    # ax1.legend(bbox_to_anchor=(1, 0.5), fontsize=15, loc='center left')
    ax1.legend(fontsize=15)

    ax2.plot(model_grid_time[list(model_grid_time.keys())[0]], n_grids, marker='x', linestyle='None', color='k')
    ax2.set_xlabel('Time (h)')
    ax2.xaxis.set_major_formatter(DateFormatter('%H'))
    ax2.set_ylabel("# of grids in source area")
    # ax2.set_xlim([datetime.datetime(2016, 5, 21, 4, 30), datetime.datetime(2016, 5, 21, 19, 30)])

    # ax3 = ax2.twinx()
    # # 50 because that is the max percentage currently coming out of the SA model repo for the example day
    # ax3.plot(model_grid_time[list(model_grid_time.keys())[0]], (np.asarray(per_covered) / 100) * 50, marker='^',
    #          linestyle='None', color='green')
    # ax3.set_ylabel("% SA covered by grid network")
    # ax3.xaxis.set_major_formatter(DateFormatter('%H'))
    # ax3.yaxis.label.set_color('green')
    # ax3.tick_params(axis='y', colors='green')

    plt.tight_layout()

    plt.savefig(savepath + str(variable) + '_detail_time_series.png',
                bbox_inches='tight')

    print('end')


def detailed_time_series_kdown(obs_time, obs_vals,
                               model_grid_time, model_grid_vals,
                               model_site_dict,
                               model_grid_time_all, model_grid_vals_all,
                               model_site_dict_all,
                               variable, savepath, DOYstart, DOYstop
                               ):
    """

    :return:
    """

    plt.rcParams.update({'font.size': 22})

    fig = plt.figure(figsize=(15, 15))

    # spec = gridspec.GridSpec(ncols=1, nrows=2,
    #                          height_ratios=[4, 1])

    spec = gridspec.GridSpec(ncols=1, nrows=1)

    ax1 = fig.add_subplot(spec[0])
    # ax2 = fig.add_subplot(spec[1])

    label_string = look_up.variable_info[variable][0]

    df_dict = {'time': obs_time, 'qh': obs_vals}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df.index = df.index.round('1s')

    five_min = df.resample('5T', closed='right', label='right').mean()
    ten_min = df.resample('10T', closed='right', label='right').mean()
    sixty_min = df.resample('60T', closed='right', label='right').mean()

    hour_1min = df.qh[np.where([i.minute == 0 for i in df.index])[0]]
    hour_5min = five_min.qh[np.where([i.minute == 0 for i in five_min.index])[0]]
    hour_10min = ten_min.qh[np.where([i.minute == 0 for i in ten_min.index])[0]]
    hour_60min = sixty_min.qh[np.where([i.minute == 0 for i in sixty_min.index])[0]]

    obs_N = len(df)

    # per_covered = list_calculated_sum(model_grid_time, percentage_covered_by_model)

    max_grid_vals_all, min_grid_vals_all, n_grids_all = variation_in_grids(model_grid_time_all, model_grid_vals_all,
                                                                           model_site_dict_all)
    ax1.fill_between(model_grid_time_all[list(model_grid_time_all.keys())[0]], max_grid_vals_all, min_grid_vals_all,
                     color='paleturquoise',
                     alpha=0.6, label='Model grid range: All')

    max_grid_vals, min_grid_vals, n_grids = variation_in_grids(model_grid_time, model_grid_vals, model_site_dict)
    ax1.fill_between(model_grid_time[list(model_grid_time.keys())[0]], max_grid_vals, min_grid_vals, color='pink',
                     alpha=0.7, label='Model grid range: In SA')

    # ax1.plot(model_grid_time['Average'], model_grid_vals['Average'], label='Average', color='red', marker='.')
    ax1.plot(model_grid_time['WAverage'], model_grid_vals['WAverage'], label='WAverage @ surface', color='blue',
             marker='.')
    ax1.plot(model_grid_time[13], model_grid_vals[13], label='Grid @ KSSW', color='green',
             marker='.')

    # Plot obs
    ax1.plot(df.index, df['qh'], linestyle='None', marker='.', color='grey', alpha=0.5,
             label="1 min obs, N = %d" % obs_N)

    ax1.plot(hour_1min.index, hour_1min.values, linestyle='None', marker='o', color='k', markersize=8,
             label="1 min obs on hour")

    ax1.plot(hour_5min.index, hour_5min.values, linestyle='None', marker='o', color='green', markersize=8,
             label="5 min obs on hour")

    ax1.plot(hour_10min.index, hour_10min.values, linestyle='None', marker='^', color='red', markersize=8,
             label="10 min obs on hour")

    ax1.plot(hour_60min.index, hour_60min.values, linestyle='None', marker='x', color='purple', markersize=8,
             label="60 min obs")

    ax1.set_ylabel(label_string)

    ax1.xaxis.set_major_formatter(DateFormatter('%H'))
    ax1.set_xlabel('Time (h)')


    # 126
    # dt.datetime(2016, 5, 5, 5, 41)
    # dt.datetime(2016, 5, 5, 18, 0)
    # ax1.set_xlim([dt.datetime(2016, 5, 5, 5, 41) - dt.timedelta(minutes=15), dt.datetime(2016, 5, 5, 18, 0) + dt.timedelta(minutes=15)])

    # 123
    # dt.datetime(2016, 5, 2, 5, 25)
    # dt.datetime(2016, 5, 2, 18, 40)
    ax1.set_xlim([dt.datetime(2016, 5, 2, 5, 25) - dt.timedelta(minutes=15), dt.datetime(2016, 5, 2, 18, 40) + dt.timedelta(minutes=15)])

    plt.gcf().autofmt_xdate()

    date_for_title = 'DOY ' + str(DOYstart)[-3:]
    # ax1.set_title(date_for_title)

    # ax1.legend(bbox_to_anchor=(1, 0.5), fontsize=15, loc='center left')
    ax1.legend(fontsize=15)

    # ax2.plot(model_grid_time[list(model_grid_time.keys())[0]], n_grids, marker='x', linestyle='None', color='k')
    # ax2.set_xlabel('Time (h)')
    # ax2.xaxis.set_major_formatter(DateFormatter('%H'))
    # ax2.set_ylabel("# of grids in source area")
    # # ax2.set_xlim([datetime.datetime(2016, 5, 21, 4, 30), datetime.datetime(2016, 5, 21, 19, 30)])

    # ax3 = ax2.twinx()
    # # 50 because that is the max percentage currently coming out of the SA model repo for the example day
    # ax3.plot(model_grid_time[list(model_grid_time.keys())[0]], (np.asarray(per_covered) / 100) * 50, marker='^',
    #          linestyle='None', color='green')
    # ax3.set_ylabel("% SA covered by grid network")
    # ax3.xaxis.set_major_formatter(DateFormatter('%H'))
    # ax3.yaxis.label.set_color('green')
    # ax3.tick_params(axis='y', colors='green')


    plt.tight_layout()

    plt.savefig(savepath + str(variable) + '_detail_time_series.png',
                bbox_inches='tight')

    print('end')


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


def plots_vars(all_days_vars, all_days_vars_10minsa):
    """
    Makes stacked plot of retrieved vars
    :param all_days_vars:
    :return:
    """

    var_dict = all_days_vars
    time = var_dict['time']
    stab_param = var_dict['stab_param']
    wind_direction = var_dict['wind_direction']
    wind_speed = var_dict['wind_speed_adj']
    kdown = var_dict['kdown']
    QH = var_dict['QH']
    area = var_dict['sa_area_km2']
    z_0 = var_dict['z_0']
    z_d = var_dict['z_d']
    z_f = var_dict['z_f']
    df_dict = {'time': time, 'QH': QH, 'z_f': z_f, 'wind_direction': wind_direction, 'wind_speed': wind_speed,
               'kdown': kdown, 'z_0': z_0, 'z_d': z_d, 'area': area, 'stab_param': stab_param}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df.index = df.index.round('1s')
    # filter out any times which are NOT unstable
    df.loc[df.stab_param > -0.03] = np.nan

    # SA 10 min data
    var_dict_10minsa = all_days_vars_10minsa
    time_10minsa = var_dict_10minsa['time']
    stab_param_10minsa = var_dict_10minsa['stab_param']
    wind_direction_10minsa = var_dict_10minsa['wind_direction']
    wind_speed_10minsa = var_dict_10minsa['wind_speed_adj']
    kdown_10minsa = var_dict_10minsa['kdown']
    QH_10minsa = var_dict_10minsa['QH']
    area_10minsa = var_dict_10minsa['sa_area_km2']
    z_0_10minsa = var_dict_10minsa['z_0']
    z_d_10minsa = var_dict_10minsa['z_d']
    z_f_10minsa = var_dict_10minsa['z_f']
    df_dict_10minsa = {'time': time_10minsa, 'QH': QH_10minsa, 'z_f': z_f_10minsa,
                       'wind_direction': wind_direction_10minsa, 'wind_speed': wind_speed_10minsa,
                       'kdown': kdown_10minsa, 'z_0': z_0_10minsa, 'z_d': z_d_10minsa, 'area': area_10minsa,
                       'stab_param': stab_param_10minsa}
    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')
    df_10minsa.index = df_10minsa.index.round('1s')
    # filter out any times which are NOT unstable
    df_10minsa.loc[df_10minsa.stab_param > -0.03] = np.nan

    # average df
    five_min = df.resample('5T', closed='right', label='right').mean()
    ten_min = df.resample('10T', closed='right', label='right').mean()
    sixty_min = df.resample('60T', closed='right', label='right').mean()

    five_min_10minsa = df_10minsa.resample('5T', closed='right', label='right').mean()
    ten_min_10minsa = df_10minsa.resample('10T', closed='right', label='right').mean()
    sixty_min_10minsa = df_10minsa.resample('60T', closed='right', label='right').mean()

    # construct title
    doy = df.index[0].strftime('%j')
    year = df.index[0].strftime('%Y')
    title_string = 'Year: ' + year + ', DOY: ' + doy

    plt.figure(figsize=(10, 70))

    spec = gridspec.GridSpec(ncols=2, nrows=4,
                             width_ratios=[2, 1])

    ax1 = plt.subplot(spec[0])
    ax3 = plt.subplot(spec[2])
    ax5 = plt.subplot(spec[4])
    ax7 = plt.subplot(spec[6])

    ax2 = plt.subplot(spec[1])
    ax4 = plt.subplot(spec[3])
    ax6 = plt.subplot(spec[5])
    ax8 = plt.subplot(spec[7])

    # LHS METEOROLOGY

    # 1 - WIND DIR
    # WD
    ax1.scatter(df_10minsa.index, df_10minsa['wind_direction'], marker='.', alpha=0.15, color='blue', s=10)
    ax1.scatter(five_min_10minsa.index, five_min_10minsa['wind_direction'], marker='o', alpha=0.4, color='green', s=10)
    ax1.scatter(ten_min_10minsa.index, ten_min_10minsa['wind_direction'], marker='^', alpha=0.7, color='red', s=10)
    ax1.scatter(sixty_min.index, sixty_min['wind_direction'], marker='x', alpha=1.0, color='purple', s=10)
    ax1.set_ylabel('Wind Direction ($^{\circ}$)')
    ax1.set_xticks([])
    ax1.set_title(title_string)

    # 2 - WIND SPEED
    ax3.scatter(df_10minsa.index, df_10minsa['wind_speed'], marker='.', alpha=0.15, color='blue', s=10)
    ax3.scatter(five_min_10minsa.index, five_min_10minsa['wind_speed'], marker='o', alpha=0.4, color='green', s=10)
    ax3.scatter(ten_min_10minsa.index, ten_min_10minsa['wind_speed'], marker='^', alpha=0.7, color='red', s=10)
    ax3.scatter(sixty_min.index, sixty_min['wind_speed'], marker='x', alpha=1.0, color='purple', s=10)
    ax3.set_ylabel('Wind Speed (m s$^{-1}$)')
    ax3.set_xticks([])

    # 3 - KDOWN
    ax5.scatter(df_10minsa.index, df_10minsa['kdown'], marker='.', alpha=0.15, color='blue', s=10)
    ax5.scatter(five_min_10minsa.index, five_min_10minsa['kdown'], marker='o', alpha=0.4, color='green', s=10)
    ax5.scatter(ten_min_10minsa.index, ten_min_10minsa['kdown'], marker='^', alpha=0.7, color='red', s=10)
    ax5.scatter(sixty_min.index, sixty_min['kdown'], marker='x', alpha=1.0, color='purple', s=10)
    ax5.set_ylabel('K$_{\downarrow}$ (W m$^{-2}$)')
    ax5.set_xticks([])

    # 4 QH
    # QH
    ax7.scatter(df_10minsa.index, df_10minsa['QH'], marker='.', label='1 min', alpha=0.15, color='blue', s=10)
    ax7.scatter(five_min_10minsa.index, five_min_10minsa['QH'], marker='o', label='5', alpha=0.4, color='green', s=10)
    ax7.scatter(ten_min_10minsa.index, ten_min_10minsa['QH'], marker='^', label='10', alpha=0.7, color='red', s=10)
    ax7.scatter(sixty_min.index, sixty_min['QH'], marker='x', label='60', alpha=1.0, color='purple', s=10)
    ax7.set_ylabel('Q$_{H}$ (W m$^{-2}$)')
    ax7.legend(frameon=False, loc='upper left')

    # RHS
    # 1 - SOURCE AREA
    ax2.plot(ten_min_10minsa.index, ten_min_10minsa['area'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax2.plot(sixty_min.index, sixty_min['area'], color='purple', marker='x')
    ax2.set_ylabel('SA area (km$^{2}$)')
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()
    ax2.set_xticks([])

    # 2 - z0
    ax4.plot(ten_min_10minsa.index, ten_min_10minsa['z_0'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax4.plot(sixty_min.index, sixty_min['z_0'], color='purple', marker='x')
    ax4.set_ylabel('z$_{0}$ (m)')
    ax4.yaxis.set_label_position("right")
    ax4.yaxis.tick_right()
    ax4.set_xticks([])

    # 3 - zd
    ax6.plot(ten_min_10minsa.index, ten_min_10minsa['z_d'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax6.plot(sixty_min.index, sixty_min['z_d'], color='purple', marker='x')
    ax6.set_ylabel('z$_{d}$ (m)')
    ax6.yaxis.set_label_position("right")
    ax6.yaxis.tick_right()
    ax6.set_xticks([])

    # 4 - zf
    ax8.plot(ten_min_10minsa.index, ten_min_10minsa['z_f'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax8.plot(sixty_min.index, sixty_min['z_f'], color='purple', marker='x')
    ax8.set_ylabel('z$_{f}$ (m)')
    ax8.yaxis.set_label_position("right")
    ax8.yaxis.tick_right()

    # plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0)

    plt.gcf().autofmt_xdate()
    ax8.set_xlabel('Time (H)')
    ax7.set_xlabel('Time (H)')

    plt.gcf().autofmt_xdate(rotation=0)
    ax8.xaxis.set_major_formatter(DateFormatter('%H'))
    ax7.xaxis.set_major_formatter(DateFormatter('%H'))
    ax1.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax2.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax3.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax4.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax5.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax6.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax7.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))
    ax8.set_xlim(min(df[~np.isnan(df['QH'])].index), max(df[~np.isnan(df['QH'])].index))

    # plt.gcf().autofmt_xdate(rotation=0)
    # ax8.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    # ax7.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    # ax1.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax2.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax3.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax4.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax5.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax6.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax7.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax8.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))

    plt.setp(ax7.get_xticklabels()[-1], visible=False)

    plt.show()

    print('end')


def plot_wind_eval(all_days_vars, all_days_vars_10minsa,
                   mod_time_ws, mod_vals_ws, mod_vals_wd, mod_height,
                   mod_vals_ws0, mod_vals_wd0, mod_height0,
                   mod_vals_ws2, mod_vals_wd2, mod_height2,
                   heath_df, LC_df, SWT_df,
                   savepath):
    """

    :param all_days_vars:
    :param all_days_vars_10minsa:
    :param mod_time_ws:
    :param mod_vals_ws:
    :param mod_vals_wd:
    :param mod_vals_ws0:
    :param mod_vals_wd0:
    :param mod_vals_ws2:
    :param mod_vals_wd2:
    :param heath_df:
    :param savepath:
    :return:
    """


    var_dict = all_days_vars
    time = var_dict['time']
    wind_direction = var_dict['wind_direction_corrected']

    wind_speed = var_dict['wind_speed_adj']
    # wind_speed = var_dict['wind_speed']
    # wind_speed_adj = var_dict['wind_speed_adj']

    df_dict = {'time': time, 'wind_direction': wind_direction, 'wind_speed': wind_speed}
    # df_dict = {'time': time, 'wind_direction': wind_direction, 'wind_speed': wind_speed, 'wind_speed_adj': wind_speed_adj}


    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df.index = df.index.round('1s')

    # SA 10 min data
    var_dict_10minsa = all_days_vars_10minsa
    time_10minsa = var_dict_10minsa['time']

    wind_direction_10minsa = var_dict_10minsa['wind_direction_corrected']

    wind_speed_10minsa = var_dict_10minsa['wind_speed_adj']
    # wind_speed_10minsa = var_dict_10minsa['wind_speed']
    # wind_speed_10minsa_adj = var_dict_10minsa['wind_speed_adj']

    df_dict_10minsa = {'time': time_10minsa, 'wind_direction': wind_direction_10minsa, 'wind_speed': wind_speed_10minsa}
    # df_dict_10minsa = {'time': time_10minsa, 'wind_direction': wind_direction_10minsa, 'wind_speed': wind_speed_10minsa, 'wind_speed_adj': wind_speed_10minsa_adj}

    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')
    df_10minsa.index = df_10minsa.index.round('1s')

    # convery wind speed and direction to u & v components, to average, then convert the averages back
    component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
    df = pd.concat([df, component_df], axis=1)

    # average df
    sixty_min = df.resample('60T', closed='right', label='right').mean()

    # get ws and dir from averaged u& v comps
    av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
    sixty_min = pd.concat([sixty_min, av_comp], axis=1)

    # do the same for the 10 min df
    component_df_10minsa = wx_u_v_components.ws_wd_to_u_v(df_10minsa['wind_speed'], df_10minsa['wind_direction'])
    df_10minsa = pd.concat([df_10minsa, component_df_10minsa], axis=1)

    five_min_10minsa = df_10minsa.resample('5T', closed='right', label='right').mean()
    ten_min_10minsa = df_10minsa.resample('10T', closed='right', label='right').mean()

    av_comp_10minsa_5 = wx_u_v_components.u_v_to_ws_wd(five_min_10minsa['u_component'], five_min_10minsa['v_component'])
    five_min_10minsa = pd.concat([five_min_10minsa, av_comp_10minsa_5], axis=1)

    av_comp_10minsa_10 = wx_u_v_components.u_v_to_ws_wd(ten_min_10minsa['u_component'], ten_min_10minsa['v_component'])
    ten_min_10minsa = pd.concat([ten_min_10minsa, av_comp_10minsa_10], axis=1)

    # construct title
    doy = df.index[0].strftime('%j')
    year = df.index[0].strftime('%Y')
    title_string = 'Year: ' + year + ', DOY: ' + doy


    plt.figure(figsize=(10, 15))

    spec = gridspec.GridSpec(ncols=1, nrows=2)

    ax1 = plt.subplot(spec[0])
    ax2 = plt.subplot(spec[1])

    # 1 - WIND DIR
    # WD
    ax1.scatter(df_10minsa.index, df_10minsa['wind_direction'], marker='.', alpha=0.15, color='blue', s=10)
    ax1.scatter(five_min_10minsa.index, five_min_10minsa['wind_direction_convert'], marker='o', alpha=0.4,
                color='green', s=10)
    ax1.scatter(ten_min_10minsa.index, ten_min_10minsa['wind_direction_convert'], marker='^', alpha=0.7, color='red',
                s=10)
    ax1.scatter(sixty_min.index, sixty_min['wind_direction_convert'], marker='x', alpha=1.0, color='purple', s=10)

    # plot heathrow and LC wind direction
    ax1.scatter(heath_df.index, heath_df['WD'], color='magenta', label='heathrow')
    ax1.scatter(LC_df.index, LC_df['WD'], color='orange', label='LC')
    ax1.scatter(SWT_df.index, SWT_df['WD'], color='blue', label='SWT')

    ax1.plot(mod_time_ws, mod_vals_wd, linewidth=1, color='blue')
    ax1.plot(mod_time_ws, mod_vals_wd0, linewidth=1, color='red')
    ax1.plot(mod_time_ws, mod_vals_wd2, linewidth=1, color='green')

    ax1.set_ylim(0, 360)

    ax1.set_ylabel('Wind Direction ($^{\circ}$)')
    ax1.set_xticks([])
    ax1.set_title(title_string)

    # 2 - WIND SPEED

    # plot heathrow wind speed
    ax2.scatter(heath_df.index, heath_df['WS'], color='magenta', label='25 m asl')
    ax2.scatter(SWT_df.index, SWT_df['WS'], color='blue', label='55 m asl')

    ax2.scatter(df_10minsa.index, df_10minsa['wind_speed'], marker='.', alpha=0.15, color='blue', s=10)
    ax2.scatter(five_min_10minsa.index, five_min_10minsa['wind_speed'], marker='o', alpha=0.4, color='green', s=10)
    ax2.scatter(ten_min_10minsa.index, ten_min_10minsa['wind_speed'], marker='^', alpha=0.7, color='red', s=10)
    ax2.scatter(sixty_min.index, sixty_min['wind_speed'], marker='x', alpha=1.0, color='purple', s=10)

    ax2.plot(mod_time_ws, mod_vals_ws, linewidth=1, color='blue', label=str(mod_height)+' aml')
    ax2.plot(mod_time_ws, mod_vals_ws0, linewidth=1, color='red', label=str(mod_height0)+' aml')
    ax2.plot(mod_time_ws, mod_vals_ws2, linewidth=1, color='green', label=str(mod_height2)+' aml')

    ax2.set_ylabel('Wind Speed (m s$^{-1}$)')

    plt.subplots_adjust(wspace=0, hspace=0)

    plt.gcf().autofmt_xdate()
    ax2.set_xlabel('Time (H)')

    plt.gcf().autofmt_xdate(rotation=0)

    ax1.set_xlim(min(df[~np.isnan(df['wind_speed'])].index), max(df[~np.isnan(df['wind_speed'])].index))
    ax2.set_xlim(min(df[~np.isnan(df['wind_speed'])].index), max(df[~np.isnan(df['wind_speed'])].index))

    # ax1.set_xlim(min(df[~np.isnan(df['wind_speed_adj'])].index), max(df[~np.isnan(df['wind_speed_adj'])].index))
    # ax2.set_xlim(min(df[~np.isnan(df['wind_speed_adj'])].index), max(df[~np.isnan(df['wind_speed_adj'])].index))

    ax2.xaxis.set_major_formatter(DateFormatter('%H'))

    # plt.legend()

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1, l1)
    ax2.legend(h2, l2)


    plt.savefig(savepath + 'test_wind.png', bbox_inches='tight')

    print('end')


def QH_over_Kdn(all_days_vars, all_days_vars_10minsa,
                   mod_kdown_time, mod_kdown_vals,
                   mod_time_ws, mod_vals_ws,
                   mod_time_wd, mod_vals_wd,
                   mod_time_qh_wav, mod_vals_qh_wav,
                   heath_df,
                   savepath):
    """

    :param all_days_vars:
    :param all_days_vars_10minsa:
    :param mod_kdown_time:
    :param mod_kdown_vals:
    :param mod_time_ws:
    :param mod_vals_ws:
    :param mod_time_wd:
    :param mod_vals_wd:
    :param mod_time_qh_wav:
    :param mod_vals_qh_wav:
    :param heath_df:
    :param savepath:
    :return:
    """

    # SA 10 min data
    var_dict_10minsa = all_days_vars_10minsa
    time_10minsa = var_dict_10minsa['time']
    stab_param_10minsa = var_dict_10minsa['stab_param']
    wind_direction_10minsa = var_dict_10minsa['wind_direction_corrected']
    wind_speed_10minsa = var_dict_10minsa['wind_speed_adj']
    kdown_10minsa = var_dict_10minsa['kdown']
    QH_10minsa = var_dict_10minsa['QH']
    area_10minsa = var_dict_10minsa['sa_area_km2']
    z_0_10minsa = var_dict_10minsa['z_0']
    z_d_10minsa = var_dict_10minsa['z_d']
    z_f_10minsa = var_dict_10minsa['z_f']
    df_dict_10minsa = {'time': time_10minsa, 'QH': QH_10minsa, 'z_f': z_f_10minsa,
                       'wind_direction': wind_direction_10minsa, 'wind_speed': wind_speed_10minsa,
                       'kdown': kdown_10minsa, 'z_0': z_0_10minsa, 'z_d': z_d_10minsa, 'area': area_10minsa,
                       'stab_param': stab_param_10minsa}
    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')
    df_10minsa.index = df_10minsa.index.round('1s')
    # filter out any times which are NOT unstable
    df_10minsa.loc[df_10minsa.stab_param > -0.03] = np.nan

    # average df
    av_df = df_10minsa.resample('15T', closed='right', label='right').mean()

    plt.plot(av_df.index, av_df.QH / av_df.kdown)
    plt.plot()

    # make a model df

    model_df_dict_kdown = {'time': mod_kdown_time, 'kdown': mod_kdown_vals}
    model_df_dict_qh = {'time': mod_time_qh_wav, 'QH': mod_vals_qh_wav}

    df_UKV_kdown = pd.DataFrame.from_dict(model_df_dict_kdown)
    df_UKV_kdown = df_UKV_kdown.set_index('time')

    df_UKV_QH = pd.DataFrame.from_dict(model_df_dict_qh)
    df_UKV_QH = df_UKV_QH.set_index('time')

    df_UKV = pd.concat([df_UKV_kdown, df_UKV_QH], axis=1)

    plt.figure(figsize=(10,10))
    plt.plot(df_UKV.index, df_UKV.QH / df_UKV.kdown, marker='.', label='UKV', color='blue')
    plt.plot(av_df.index, av_df.QH / av_df.kdown, marker='.', label='15 min av obs', color='orange')

    plt.gca().xaxis.set_major_formatter(DateFormatter('%H'))

    plt.legend()

    plt.ylabel('$Q_{H}$ / $K_{\downarrow}$')
    plt.xlabel('Time (H)')

    # plt.show()

    print('end')


def plots_vars_mod(all_days_vars, all_days_vars_10minsa,
                   mod_kdown_time, mod_kdown_vals,
                   mod_time_ws, mod_vals_ws,
                   mod_time_wd, mod_vals_wd,
                   mod_time_qh_wav, mod_vals_qh_wav,
                   heath_df,
                   savepath):
    """
    Makes stacked plot of retrieved vars
    :param all_days_vars:
    :return:
    """

    var_dict = all_days_vars
    time = var_dict['time']
    stab_param = var_dict['stab_param']
    wind_direction = var_dict['wind_direction_corrected']
    wind_speed = var_dict['wind_speed_adj']
    kdown = var_dict['kdown']
    QH = var_dict['QH']
    area = var_dict['sa_area_km2']
    z_0 = var_dict['z_0']
    z_d = var_dict['z_d']
    z_f = var_dict['z_f']
    df_dict = {'time': time, 'QH': QH, 'z_f': z_f, 'wind_direction': wind_direction, 'wind_speed': wind_speed,
               'kdown': kdown, 'z_0': z_0, 'z_d': z_d, 'area': area, 'stab_param': stab_param}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df.index = df.index.round('1s')
    # filter out any times which are NOT unstable
    df.loc[df.stab_param > -0.03] = np.nan

    # SA 10 min data
    var_dict_10minsa = all_days_vars_10minsa
    time_10minsa = var_dict_10minsa['time']
    stab_param_10minsa = var_dict_10minsa['stab_param']
    wind_direction_10minsa = var_dict_10minsa['wind_direction_corrected']
    wind_speed_10minsa = var_dict_10minsa['wind_speed_adj']
    kdown_10minsa = var_dict_10minsa['kdown']
    QH_10minsa = var_dict_10minsa['QH']
    area_10minsa = var_dict_10minsa['sa_area_km2']
    z_0_10minsa = var_dict_10minsa['z_0']
    z_d_10minsa = var_dict_10minsa['z_d']
    z_f_10minsa = var_dict_10minsa['z_f']
    df_dict_10minsa = {'time': time_10minsa, 'QH': QH_10minsa, 'z_f': z_f_10minsa,
                       'wind_direction': wind_direction_10minsa, 'wind_speed': wind_speed_10minsa,
                       'kdown': kdown_10minsa, 'z_0': z_0_10minsa, 'z_d': z_d_10minsa, 'area': area_10minsa,
                       'stab_param': stab_param_10minsa}
    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')
    df_10minsa.index = df_10minsa.index.round('1s')
    # filter out any times which are NOT unstable
    df_10minsa.loc[df_10minsa.stab_param > -0.03] = np.nan

    # set wind direction column to nan when there are no wind speed data (which will only be there for unstable periods,
    # as they have gone through a correction process dependent on stability)
    df_10minsa['wind_direction'].iloc[np.where(np.isnan(df_10minsa['wind_speed']))] = np.nan

    # convery wind speed and direction to u & v components, to average, then convert the averages back
    component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])
    df = pd.concat([df, component_df], axis=1)

    # average df
    sixty_min = df.resample('60T', closed='right', label='right').mean()

    # get ws and dir from averaged u& v comps
    av_comp = wx_u_v_components.u_v_to_ws_wd(sixty_min['u_component'], sixty_min['v_component'])
    sixty_min = pd.concat([sixty_min, av_comp], axis=1)

    # do the same for the 10 min df
    component_df_10minsa = wx_u_v_components.ws_wd_to_u_v(df_10minsa['wind_speed'], df_10minsa['wind_direction'])
    df_10minsa = pd.concat([df_10minsa, component_df_10minsa], axis=1)

    five_min_10minsa = df_10minsa.resample('5T', closed='right', label='right').mean()
    ten_min_10minsa = df_10minsa.resample('10T', closed='right', label='right').mean()

    av_comp_10minsa_5 = wx_u_v_components.u_v_to_ws_wd(five_min_10minsa['u_component'], five_min_10minsa['v_component'])
    five_min_10minsa = pd.concat([five_min_10minsa, av_comp_10minsa_5], axis=1)

    av_comp_10minsa_10 = wx_u_v_components.u_v_to_ws_wd(ten_min_10minsa['u_component'], ten_min_10minsa['v_component'])
    ten_min_10minsa = pd.concat([ten_min_10minsa, av_comp_10minsa_10], axis=1)

    wind_av_whole_day_df = pd.DataFrame.from_dict(
        {'u_component': [df_10minsa.mean()['u_component']], 'v_component': [df_10minsa.mean()['v_component']]})
    wind_av_whole_day_comp = wx_u_v_components.u_v_to_ws_wd(wind_av_whole_day_df['u_component'], wind_av_whole_day_df['v_component'])

    # construct title
    doy = df.index[0].strftime('%j')
    year = df.index[0].strftime('%Y')
    title_string = 'Year: ' + year + ', DOY: ' + doy

    plt.figure(figsize=(10, 15))

    spec = gridspec.GridSpec(ncols=2, nrows=4,
                             width_ratios=[2, 1])

    ax1 = plt.subplot(spec[0])
    ax3 = plt.subplot(spec[2])
    ax5 = plt.subplot(spec[4])
    ax7 = plt.subplot(spec[6])

    ax2 = plt.subplot(spec[1])
    ax4 = plt.subplot(spec[3])
    ax6 = plt.subplot(spec[5])
    ax8 = plt.subplot(spec[7])

    # LHS METEOROLOGY

    # 1 - WIND DIR
    # WD
    ax1.scatter(df_10minsa.index, df_10minsa['wind_direction'], marker='.', alpha=0.15, color='blue', s=10)
    ax1.scatter(five_min_10minsa.index, five_min_10minsa['wind_direction_convert'], marker='o', alpha=0.4,
                color='green', s=10)
    ax1.scatter(ten_min_10minsa.index, ten_min_10minsa['wind_direction_convert'], marker='^', alpha=0.7, color='red',
                s=10)
    ax1.scatter(sixty_min.index, sixty_min['wind_direction_convert'], marker='x', alpha=1.0, color='purple', s=10)

    # plot heathrow wind direction
    # ax1.scatter(heath_df.index, heath_df['WD'], color='magenta')

    ax1.plot(mod_time_wd, mod_vals_wd, linewidth=1, color='blue')

    ax1.set_ylim(0, 360)

    ax1.set_ylabel('Wind Direction ($^{\circ}$)')
    ax1.set_xticks([])
    ax1.set_title(title_string)

    # 2 - WIND SPEED
    ax3.scatter(df_10minsa.index, df_10minsa['wind_speed'], marker='.', alpha=0.15, color='blue', s=10)
    ax3.scatter(five_min_10minsa.index, five_min_10minsa['wind_speed'], marker='o', alpha=0.4, color='green', s=10)
    ax3.scatter(ten_min_10minsa.index, ten_min_10minsa['wind_speed'], marker='^', alpha=0.7, color='red', s=10)
    ax3.scatter(sixty_min.index, sixty_min['wind_speed'], marker='x', alpha=1.0, color='purple', s=10)

    ax3.plot(mod_time_ws, mod_vals_ws, linewidth=1, color='blue')

    ax3.set_ylabel('Wind Speed (m s$^{-1}$)')
    ax3.set_xticks([])

    # 3 - KDOWN
    ax5.scatter(df_10minsa.index, df_10minsa['kdown'], marker='.', alpha=0.15, color='blue', s=10)
    ax5.scatter(five_min_10minsa.index, five_min_10minsa['kdown'], marker='o', alpha=0.4, color='green', s=10)
    ax5.scatter(ten_min_10minsa.index, ten_min_10minsa['kdown'], marker='^', alpha=0.7, color='red', s=10)
    ax5.scatter(sixty_min.index, sixty_min['kdown'], marker='x', alpha=1.0, color='purple', s=10)

    ax5.plot(mod_kdown_time + dt.timedelta(minutes=15), mod_kdown_vals, linewidth=1, color='blue')

    ax5.set_ylabel('K$_{\downarrow}$ (W m$^{-2}$)')
    ax5.set_xticks([])

    # 4 QH
    # QH
    ax7.scatter(df_10minsa.index, df_10minsa['QH'], marker='.', label='1 min', alpha=0.15, color='blue', s=10)
    ax7.scatter(five_min_10minsa.index, five_min_10minsa['QH'], marker='o', label='5', alpha=0.4, color='green', s=10)
    ax7.scatter(ten_min_10minsa.index, ten_min_10minsa['QH'], marker='^', label='10', alpha=0.7, color='red', s=10)
    ax7.scatter(sixty_min.index, sixty_min['QH'], marker='x', label='60', alpha=1.0, color='purple', s=10)

    ax7.plot(mod_time_qh_wav, mod_vals_qh_wav, linewidth=1, color='blue', label='UKV')

    ax7.set_ylabel('Q$_{H}$ (W m$^{-2}$)')
    ax7.legend(frameon=False, loc='upper left')

    # RHS
    # 1 - SOURCE AREA
    ax2.plot(ten_min_10minsa.index, ten_min_10minsa['area'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax2.plot(sixty_min.index, sixty_min['area'], color='purple', marker='x')
    ax2.set_ylabel('SA area (km$^{2}$)')
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()
    ax2.set_xticks([])

    # 2 - z0
    ax4.plot(ten_min_10minsa.index, ten_min_10minsa['z_0'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax4.plot(sixty_min.index, sixty_min['z_0'], color='purple', marker='x')
    ax4.set_ylabel('z$_{0}$ (m)')
    ax4.yaxis.set_label_position("right")
    ax4.yaxis.tick_right()
    ax4.set_xticks([])

    # 3 - zd
    ax6.plot(ten_min_10minsa.index, ten_min_10minsa['z_d'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax6.plot(sixty_min.index, sixty_min['z_d'], color='purple', marker='x')
    ax6.set_ylabel('z$_{d}$ (m)')
    ax6.yaxis.set_label_position("right")
    ax6.yaxis.tick_right()
    ax6.set_xticks([])

    # 4 - zf
    ax8.plot(ten_min_10minsa.index, ten_min_10minsa['z_f'], color='red', marker='^', alpha=0.3, linewidth=0.5)
    ax8.plot(sixty_min.index, sixty_min['z_f'], color='purple', marker='x')
    ax8.set_ylabel('z$_{f}$ (m)')
    ax8.yaxis.set_label_position("right")
    ax8.yaxis.tick_right()

    # plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0)

    plt.gcf().autofmt_xdate()
    ax8.set_xlabel('Time (H)')
    ax7.set_xlabel('Time (H)')

    plt.gcf().autofmt_xdate(rotation=0)
    ax8.xaxis.set_major_formatter(DateFormatter('%H'))
    ax7.xaxis.set_major_formatter(DateFormatter('%H'))

    ax1.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax2.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax3.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax4.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax5.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax6.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax7.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))
    ax8.set_xlim(min(df_10minsa[~np.isnan(df_10minsa['QH'])].index), max(df[~np.isnan(df_10minsa['QH'])].index))

    # plt.gcf().autofmt_xdate(rotation=0)
    # ax8.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    # ax7.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    # ax1.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax2.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax3.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax4.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax5.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax6.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax7.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))
    # ax8.set_xlim(min(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index), max(ten_min_10minsa[~np.isnan(ten_min_10minsa['z_f'])].index))

    plt.setp(ax7.get_xticklabels()[-1], visible=False)

    plt.savefig(savepath + 'test.png', bbox_inches='tight')

    print('end')


def qh_comparison(all_days_vars, all_days_vars_10minsa):
    """

    :param all_days_vars:
    :param all_days_vars_10minsa:
    :return:
    """

    var_dict = all_days_vars
    var_dict_10minsa = all_days_vars_10minsa

    time = var_dict['time']
    time_10minsa = var_dict_10minsa['time']

    QH = var_dict['QH']
    QH_10minsa = var_dict_10minsa['QH']

    z_d = var_dict['z_d']
    z_d_10minsa = var_dict_10minsa['z_d']

    z_0 = var_dict['z_0']
    z_0_10minsa = var_dict_10minsa['z_0']

    z_f = var_dict['z_f']
    z_f_10minsa = var_dict_10minsa['z_f']

    df_dict = {'time': time, 'QH': QH, 'z_d': z_d, 'z_0': z_0, 'z_f': z_f}
    df_dict_10minsa = {'time': time_10minsa, 'QH': QH_10minsa, 'z_0': z_0_10minsa, 'z_d': z_d_10minsa,
                       'z_f': z_f_10minsa}

    df = pd.DataFrame(df_dict)
    df = df.set_index('time')

    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')

    # index of where the 2 dfs are the same
    ind_same = np.where(df['QH'] - df_10minsa['QH'] == 0)[0]
    # remove these
    df['QH'].iloc[ind_same] = np.nan
    df_10minsa['QH'].iloc[ind_same] = np.nan

    # ind_same_zd = np.where(df['z_d'] - df_10minsa['z_d'] == 0)[0]
    # ind_same_z0 = np.where(df['z_0'] - df_10minsa['z_0'] == 0)[0]
    # ind_same_zf = np.where(df['z_f'] - df_10minsa['z_f'] == 0)[0]
    # df['z_d'].iloc[ind_same_zd] = np.nan
    # df_10minsa['z_d'].iloc[ind_same_zd] = np.nan
    # df['z_0'].iloc[ind_same_z0] = np.nan
    # df_10minsa['z_0'].iloc[ind_same_z0] = np.nan
    # df['z_f'].iloc[ind_same_zf] = np.nan
    # df_10minsa['z_f'].iloc[ind_same_zf] = np.nan

    plt.figure(figsize=(10, 10))
    ax1 = plt.subplot(3, 1, 1)
    ax2 = plt.subplot(3, 1, 2)
    ax3 = plt.subplot(3, 1, 3)

    ax1.scatter(df.index, df['QH'], marker='+', label='hour', color='green')
    ax1.scatter(df_10minsa.index, df_10minsa['QH'], marker='x', label='10 min', color='orange')
    ax1.set_xticks([])
    ax1.set_ylabel('$Q_{H}$ ($W m^{-2}$)')
    ax1.legend()

    ax2.scatter(df.index, (df_10minsa['QH'] - df['QH']) / df['QH'], color='k', marker='.')
    ax2.set_ylabel('($Q_{H}^{10min}$ - $Q_{H}^{hour}$) / $Q_{H}^{hour}$')

    ax3.scatter(df.index, (df_10minsa['z_d'] - df['z_d']) / df['z_d'], color='blue', marker='.', label='$z_{d}$')
    ax3.scatter(df.index, (df_10minsa['z_0'] - df['z_0']) / df['z_d'], color='red', marker='.', label='$z_{0}$')
    ax3.scatter(df.index, (df_10minsa['z_f'] - df['z_f']) / df['z_f'], color='green', marker='.', label='$z_{f}$')
    ax3.set_ylabel('($z^{10min}$ - $z^{hour}$) / $z^{hour}$')
    ax3.legend()
    # ax3.set_ylabel('($z_{d}^{10min}$ - $z_{d}^{hour}$) / $z_{d}^{hour}$')
    # ax3.yaxis.label.set_color('blue')

    # ax4 = ax3.twinx()
    # ax4.scatter(df.index, (df_10minsa['z_0'] - df['z_0']) / df['z_d'], color='red', marker='.', label='$z_{0}$')
    # ax4.set_ylabel('($z_{0}^{10min}$ - $z_{0}^{hour}$) / $z_{0}^{hour}$')
    # ax4.yaxis.label.set_color('red')

    ax1.set_xlim(
        min(min(df[~np.isnan(df['QH'])].index),
            min(df_10minsa[~np.isnan(df_10minsa['QH'])].index)) - datetime.timedelta(minutes=10),
        max(max(df[~np.isnan(df['QH'])].index),
            max(df_10minsa[~np.isnan(df_10minsa['QH'])].index)) + datetime.timedelta(minutes=10))
    ax2.set_xlim(
        min(min(df[~np.isnan(df['QH'])].index),
            min(df_10minsa[~np.isnan(df_10minsa['QH'])].index)) - datetime.timedelta(minutes=10),
        max(max(df[~np.isnan(df['QH'])].index),
            max(df_10minsa[~np.isnan(df_10minsa['QH'])].index)) + datetime.timedelta(minutes=10))
    ax3.set_xlim(
        min(min(df[~np.isnan(df['QH'])].index),
            min(df_10minsa[~np.isnan(df_10minsa['QH'])].index)) - datetime.timedelta(minutes=10),
        max(max(df[~np.isnan(df['QH'])].index),
            max(df_10minsa[~np.isnan(df_10minsa['QH'])].index)) + datetime.timedelta(minutes=10))

    ax1.set_ylim(np.nanmin(df_10minsa['QH']) - 10, np.nanmax(df_10minsa['QH']) + 10)

    plt.subplots_adjust(wspace=0, hspace=0)

    # plt.gcf().autofmt_xdate(rotation=0)
    plt.gcf().autofmt_xdate()
    ax3.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax3.set_xlabel('Time (H:M)')

    plt.show()

    print('end')


def qh_vs_zf(all_days_vars, all_days_vars_10minsa):
    """

    :param all_days_vars:
    :param all_days_vars_10minsa:
    :return:
    """

    var_dict = all_days_vars
    var_dict_10minsa = all_days_vars_10minsa

    time = var_dict['time']
    time_10minsa = var_dict_10minsa['time']

    QH = var_dict['QH']
    QH_10minsa = var_dict_10minsa['QH']

    z_f = var_dict['z_f']
    z_f_10minsa = var_dict_10minsa['z_f']

    df_dict = {'time': time, 'QH': QH, 'z_f': z_f}
    df_dict_10minsa = {'time': time_10minsa, 'QH': QH_10minsa,
                       'z_f': z_f_10minsa}

    df = pd.DataFrame(df_dict)
    df = df.set_index('time')

    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')

    df = df.dropna()
    df_10minsa = df_10minsa.dropna()

    # # index of where the 2 dfs are the same
    # ind_same = np.where(df['QH'] - df_10minsa['QH'] == 0)[0]
    # # remove these
    # df['QH'].iloc[ind_same] = np.nan
    # df_10minsa['QH'].iloc[ind_same] = np.nan
    # ind_same_zf = np.where(df['z_f'] - df_10minsa['z_f'] == 0)[0]
    # df['z_f'].iloc[ind_same_zf] = np.nan
    # df_10minsa['z_f'].iloc[ind_same_zf] = np.nan

    if len(df.index) > len(df_10minsa.index):
        bigger_df = df
    else:
        bigger_df = df_10minsa

    fig, ax = plt.subplots(figsize=(7, 7))

    # identity line
    plt.plot((df_10minsa['z_f'] - df['z_f']) / df['z_f'], (df_10minsa['z_f'] - df['z_f']) / df['z_f'], color='k',
             linewidth='0.5')
    plt.axhline(y=0, color='grey', linestyle=':', linewidth=0.5)
    plt.axvline(x=0, color='grey', linestyle=':', linewidth=0.5)

    s = ax.scatter((df_10minsa['z_f'] - df['z_f']) / df['z_f'], (df_10minsa['QH'] - df['QH']) / df['QH'],
                   marker='.', c=mdates.date2num(bigger_df.index))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    cbar = fig.colorbar(mappable=s, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(df.index[np.where(bigger_df.index.minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (H)')

    ax.set_ylabel('($Q_{H}^{10min}$ - $Q_{H}^{hour}$) / $Q_{H}^{hour}$')
    ax.set_xlabel('($z_{f}^{10min}$ - $z_{f}^{hour}$) / $z_{f}^{hour}$')

    plt.show()

    print('end')


def qh_vs_zf_both_days(all_days_vars, all_days_vars_10minsa, all_days_vars_142, all_days_vars_10minsa_142):
    """

    :param all_days_vars:
    :param all_days_vars_10minsa:
    :return:
    """

    plt.close('all')

    var_dict = all_days_vars
    var_dict_10minsa = all_days_vars_10minsa
    time = var_dict['time']
    time_10minsa = var_dict_10minsa['time']
    QH = var_dict['QH']
    QH_10minsa = var_dict_10minsa['QH']
    z_f = var_dict['z_f']
    z_f_10minsa = var_dict_10minsa['z_f']
    df_dict = {'time': time, 'QH': QH, 'z_f': z_f}
    df_dict_10minsa = {'time': time_10minsa, 'QH': QH_10minsa,
                       'z_f': z_f_10minsa}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df.index = df.index.round('1s')
    df_10minsa = pd.DataFrame(df_dict_10minsa)
    df_10minsa = df_10minsa.set_index('time')
    df_10minsa.index = df_10minsa.index.round('1s')
    df = df.dropna()
    df_10minsa = df_10minsa.dropna()

    var_dict_142 = all_days_vars_142
    var_dict_10minsa_142 = all_days_vars_10minsa_142
    time_142 = var_dict_142['time']
    time_10minsa_142 = var_dict_10minsa_142['time']
    QH_142 = var_dict_142['QH']
    QH_10minsa_142 = var_dict_10minsa_142['QH']
    z_f_142 = var_dict_142['z_f']
    z_f_10minsa_142 = var_dict_10minsa_142['z_f']
    df_dict_142 = {'time': time_142, 'QH': QH_142, 'z_f': z_f_142}
    df_dict_10minsa_142 = {'time': time_10minsa_142, 'QH': QH_10minsa_142,
                           'z_f': z_f_10minsa_142}
    df_142 = pd.DataFrame(df_dict_142)
    df_142 = df_142.set_index('time')
    df_142.index = df_142.index.round('1s')
    df_10minsa_142 = pd.DataFrame(df_dict_10minsa_142)
    df_10minsa_142 = df_10minsa_142.set_index('time')
    df_10minsa_142.index = df_10minsa_142.index.round('1s')
    df_142 = df_142.dropna()
    df_10minsa_142 = df_10minsa_142.dropna()

    df.columns = ['QH_111_hour', 'z_f_111_hour']
    df_10minsa.columns = ['QH_111_10min', 'z_f_111_10min']

    df_142.columns = ['QH_142_hour', 'z_f_142_hour']
    df_10minsa_142.columns = ['QH_142_10min', 'z_f_142_10min']

    combine_df_111 = pd.concat([df, df_10minsa], axis=1)
    combine_df_142 = pd.concat([df_142, df_10minsa_142], axis=1)

    format_index_142 = combine_df_142.index.strftime('%H:%M')
    format_index_111 = combine_df_111.index.strftime('%H:%M')

    index_list_142 = []
    # construct datetime obj for both days with same year day etc. (for colourbar)
    for i in format_index_142:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_142.append(datetime_object)
    index_list_111 = []
    for i in format_index_111:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_111.append(datetime_object)

    combine_df_142.index = index_list_142
    combine_df_111.index = index_list_111

    combine_df = pd.concat([combine_df_111, combine_df_142], axis=1)


    time_grouper = pd.Grouper(freq='10T', closed='left', label='left', offset='1min')
    time_groups = combine_df.groupby(time_grouper)



    start_times_111 = []
    x_vals_111 = []
    y_vals_111 = []
    IQR25_vals_111 = []
    IQR75_vals_111 = []
    mean_flux_111 = []


    for start_time, time_group in time_groups:

        time_group['x_axis_vals'] = (time_group['z_f_111_10min'] - time_group['z_f_111_hour']) / time_group['z_f_111_hour']
        x_axis_vals = time_group['x_axis_vals']
        x_axis_vals = x_axis_vals.dropna()

        # check that all 10 min zf vals in the column are the same
        if len(x_axis_vals) == 0:
            continue
        else:
            assert (x_axis_vals[0] == x_axis_vals).all()

        x_axis_val = x_axis_vals[0]

        time_group['y_axis_vals'] = (time_group['QH_111_10min'] - time_group['QH_111_hour']) / time_group['QH_111_hour']
        y_axis_vals = time_group['y_axis_vals']

        median = y_axis_vals.median()

        IQR_25 = y_axis_vals.quantile(.25)
        IQR_75 = y_axis_vals.quantile(.75)

        mean_flux = np.nanmean(time_group['QH_111_10min'])

        start_times_111.append(start_time)
        x_vals_111.append(x_axis_val)
        y_vals_111.append(median)
        IQR25_vals_111.append(IQR_25)
        IQR75_vals_111.append(IQR_75)
        mean_flux_111.append(mean_flux)



    ##########################
    start_times_142 = []
    x_vals_142 = []
    y_vals_142 = []
    IQR25_vals_142 = []
    IQR75_vals_142 = []
    mean_flux_142 = []

    for start_time, time_group in time_groups:

        time_group['x_axis_vals'] = (time_group['z_f_142_10min'] - time_group['z_f_142_hour']) / time_group[
            'z_f_142_hour']
        x_axis_vals = time_group['x_axis_vals']
        x_axis_vals = x_axis_vals.dropna()

        # check that all 10 min zf vals in the column are the same
        if len(x_axis_vals) == 0:
            continue
        else:
            assert (x_axis_vals[0] == x_axis_vals).all()

        x_axis_val = x_axis_vals[0]

        time_group['y_axis_vals'] = (time_group['QH_142_10min'] - time_group['QH_142_hour']) / time_group['QH_142_hour']
        y_axis_vals = time_group['y_axis_vals']

        median = y_axis_vals.median()

        IQR_25 = y_axis_vals.quantile(.25)
        IQR_75 = y_axis_vals.quantile(.75)

        mean_flux = np.nanmean(time_group['QH_142_10min'])

        start_times_142.append(start_time)
        x_vals_142.append(x_axis_val)
        y_vals_142.append(median)
        IQR25_vals_142.append(IQR_25)
        IQR75_vals_142.append(IQR_75)
        mean_flux_142.append(mean_flux)


    fig, ax = plt.subplots(figsize=(12, 12))

    # identity line
    plt.plot((combine_df['z_f_111_10min'] - combine_df['z_f_111_hour']) / combine_df['z_f_111_hour'],
             (combine_df['z_f_111_10min'] - combine_df['z_f_111_hour']) / combine_df['z_f_111_hour'], color='k',
             linewidth='0.5')
    plt.axhline(y=0, color='grey', linestyle=':', linewidth=0.5)
    plt.axvline(x=0, color='grey', linestyle=':', linewidth=0.5)


    bellow_50_142_index = np.where(np.asarray(mean_flux_142) < 75)[0]
    bellow_50_111_index = np.where(np.asarray(mean_flux_111) < 75)[0]

    circ_142 = ax.scatter(np.asarray(x_vals_142)[bellow_50_142_index], np.asarray(y_vals_142)[bellow_50_142_index],
                          marker='o', facecolors='none', s=80, edgecolors='k', alpha=0.5, label='$\overline{Q_{H}^{10 min}}$ < 75 $W$ $m^{-2}$')

    circ_111 = ax.scatter(np.asarray(x_vals_111)[bellow_50_111_index], np.asarray(y_vals_111)[bellow_50_111_index],
                          marker='o', facecolors='none', s=80, edgecolors='k', alpha=0.5)


    cmap = cm.get_cmap('rainbow')

    earliest_time = min([start_times_142[0], start_times_111[0]])
    latest_time = max([start_times_142[-1], start_times_111[-1]])

    bounds = np.linspace(mdates.date2num(earliest_time), mdates.date2num(latest_time), len(start_times_142)+1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    smap = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    list_of_rgba_111 = smap.to_rgba(mdates.date2num(start_times_111))
    list_of_rgba_142 = smap.to_rgba(mdates.date2num(start_times_142))

    for i in range(0, len(start_times_142)):
        ax.vlines(x_vals_142[i], IQR25_vals_142[i], IQR75_vals_142[i], color=list_of_rgba_142[i])

    for i in range(0, len(start_times_111)):
        ax.vlines(x_vals_111[i], IQR25_vals_111[i], IQR75_vals_111[i], color=list_of_rgba_111[i])


    s = ax.scatter(x_vals_142, y_vals_142, c=mdates.date2num(start_times_142), marker='x', cmap=cmap, norm=norm, edgecolor='None', label='Cloudy')
    s2 = ax.scatter(x_vals_111, y_vals_111, c=mdates.date2num(start_times_111), marker='o', cmap=cmap, norm=norm, edgecolor='None', label='Clear')

    x_vals_both = x_vals_142 + x_vals_111
    y_vals_both = y_vals_142 + y_vals_111
    gradient, intercept, r_value, p_value, std_err = stats.linregress(x_vals_both, y_vals_both)

    string_for_label = 'm = ' + '%s' % float('%.5g' % gradient) + '\n c = ' + '%s' % float('%.5g' % intercept)
    mn = np.min(x_vals_both)
    mx = np.max(x_vals_both)
    x1 = np.linspace(mn, mx, 500)
    y1 = gradient * x1 + intercept
    plt.plot(x1, y1, '--r', label=string_for_label)


    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    cbar = fig.colorbar(mappable=s2, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(combine_df.index[np.where(combine_df.index.minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (H)')

    ax.set_ylabel('($Q_{H}^{10min}$ - $Q_{H}^{hour}$) / $Q_{H}^{hour}$')
    ax.set_xlabel('($z_{f}^{10min}$ - $z_{f}^{hour}$) / $z_{f}^{hour}$')

    leg = ax.legend(frameon=False, fontsize = 'medium')

    t1, t2, t3, t4 = leg.get_texts()
    # here we create the distinct instance
    t1._fontproperties = t2._fontproperties.copy()
    t1.set_size('small')

    plt.savefig('C:/Users/beths/Desktop/LANDING/yeet.png', bbox_inches='tight')

    print('end')








    """

    fig, ax = plt.subplots(figsize=(7, 7))

    # identity line
    plt.plot((combine_df['z_f_111_10min'] - combine_df['z_f_111_hour']) / combine_df['z_f_111_hour'],
             (combine_df['z_f_111_10min'] - combine_df['z_f_111_hour']) / combine_df['z_f_111_hour'], color='k',
             linewidth='0.5')
    plt.axhline(y=0, color='grey', linestyle=':', linewidth=0.5)
    plt.axvline(x=0, color='grey', linestyle=':', linewidth=0.5)

    # 111
    bellow_50_111_index = np.where(combine_df.QH_111_hour < 50)[0]

    circ_111 = ax.scatter(
        (combine_df['z_f_111_10min'][bellow_50_111_index] - combine_df['z_f_111_hour'][bellow_50_111_index]) /
        combine_df['z_f_111_hour'][bellow_50_111_index],
        (combine_df['QH_111_10min'][bellow_50_111_index] - combine_df['QH_111_hour'][bellow_50_111_index]) /
        combine_df['QH_111_hour'][bellow_50_111_index],
        marker='o', facecolors='none', s=80, edgecolors='k', alpha=0.5)

    # 142
    bellow_50_142_index = np.where(combine_df.QH_142_hour < 50)[0]

    circ_142 = ax.scatter(
        (combine_df['z_f_142_10min'][bellow_50_142_index] - combine_df['z_f_142_hour'][bellow_50_142_index]) /
        combine_df['z_f_142_hour'][bellow_50_142_index],
        (combine_df['QH_142_10min'][bellow_50_142_index] - combine_df['QH_142_hour'][bellow_50_142_index]) /
        combine_df['QH_142_hour'][bellow_50_142_index],
        marker='o', facecolors='none', s=80, edgecolors='k', alpha=0.5, label='$Q_{H}^{hour}$ < 50 $W$ $m^{-2}$')


    # 111
    s = ax.scatter((combine_df['z_f_111_10min'] - combine_df['z_f_111_hour']) / combine_df['z_f_111_hour'],
                   (combine_df['QH_111_10min'] - combine_df['QH_111_hour']) / combine_df['QH_111_hour'],
                   marker='+', c=mdates.date2num(combine_df.index), label='126', cmap=plt.cm.rainbow, s=20)

    # 142
    s2 = ax.scatter((combine_df['z_f_142_10min'] - combine_df['z_f_142_hour']) / combine_df['z_f_142_hour'],
                    (combine_df['QH_142_10min'] - combine_df['QH_142_hour']) / combine_df['QH_142_hour'],
                    marker='x', c=mdates.date2num(combine_df.index), label='123', cmap=plt.cm.rainbow, s=20)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    cbar = fig.colorbar(mappable=s2, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(combine_df.index[np.where(combine_df.index.minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (H)')

    ax.set_ylabel('($Q_{H}^{10min}$ - $Q_{H}^{hour}$) / $Q_{H}^{hour}$')
    ax.set_xlabel('($z_{f}^{10min}$ - $z_{f}^{hour}$) / $z_{f}^{hour}$')

    ax.legend(frameon=False)

    plt.show()
    
    """

    print('end')


def find_mean_zf_both_days(all_days_vars_10minsa, all_days_vars_10minsa_142):
    """

    :param all_days_vars:
    :return:
    """

    var_dict = all_days_vars_10minsa
    time = var_dict['time']
    z_f = var_dict['z_f']
    df_dict = {'time': time, 'z_f': z_f}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df = df.dropna()
    df.index = df.index.round('1s')

    var_dict_142 = all_days_vars_10minsa_142
    time_142 = var_dict_142['time']
    z_f_142 = var_dict_142['z_f']
    df_dict_142 = {'time': time_142, 'z_f': z_f_142}
    df_142 = pd.DataFrame(df_dict_142)
    df_142 = df_142.set_index('time')
    df_142 = df_142.dropna()
    df_142.index = df_142.index.round('1s')

    ten_min = df.resample('10T', closed='right', label='right').mean()

    ten_min_142 = df_142.resample('10T', closed='right', label='right').mean()

    combine_ten_min = pd.concat([ten_min, ten_min_142])

    sixty_min = combine_ten_min.resample('60T', closed='right', label='right').mean()
    n_samples_hour = np.cumsum(combine_ten_min.resample('60T', closed='right', label='right').count()['z_f'])

    z_f_list = combine_ten_min['z_f'].to_list()

    z_f_mean = []
    z_f_append = []
    n_samples = []

    for zf in z_f_list:
        # append new zf value to the append list
        z_f_append.append(zf)

        # caclualte mean of the append list
        zf_mean = np.mean(z_f_append)

        # append mean to mean list
        z_f_mean.append(zf_mean)

        # append len to the n_samples list
        n_samples.append(len(z_f_append))

    plt.figure(figsize=(10, 6))

    ax1 = plt.subplot(1, 1, 1)

    ax1.plot(n_samples, z_f_mean, marker='.', color='blue', label='Moving $z_{f}^{\overline{SA}}$')
    ax1.scatter(n_samples_hour, sixty_min['z_f'], color='green', label='$\overline{z_{f}}$ per hour')
    ax1.scatter(len(z_f_mean), np.mean(combine_ten_min['z_f']), marker='x', color='red', label='Total av')

    ax1.legend()

    ax1.set_ylabel('$z_{f}$ (m)')

    ax1.set_xlabel('n samples')

    plt.show()

    print('end')


def find_mean_zf(all_days_vars_10minsa):
    """

    :param all_days_vars:
    :return:
    """

    var_dict = all_days_vars_10minsa

    time = var_dict['time']

    z_f = var_dict['z_f']

    df_dict = {'time': time, 'z_f': z_f}

    df = pd.DataFrame(df_dict)
    df = df.set_index('time')

    df = df.dropna()

    df.index = df.index.round('1s')

    ten_min = df.resample('10T', closed='right', label='right').mean()
    sixty_min = ten_min.resample('60T', closed='right', label='right').mean()

    n_samples_hour = np.cumsum(ten_min.resample('60T', closed='right', label='right').count()['z_f'])

    z_f_list = ten_min['z_f'].to_list()

    z_f_mean = []
    z_f_append = []
    n_samples = []

    for zf in z_f_list:
        # append new zf value to the append list
        z_f_append.append(zf)

        # caclualte mean of the append list
        zf_mean = np.mean(z_f_append)

        # append mean to mean list
        z_f_mean.append(zf_mean)

        # append len to the n_samples list
        n_samples.append(len(z_f_append))

    plt.figure(figsize=(10, 6))

    ax1 = plt.subplot(1, 1, 1)

    ax1.plot(n_samples, z_f_mean, marker='.', color='blue', label='Moving $z_{f}^{\overline{SA}}$')
    ax1.scatter(n_samples_hour, sixty_min['z_f'], color='green', label='$\overline{z_{f}}$ per hour')
    ax1.scatter(len(z_f_mean), np.mean(ten_min['z_f']), marker='x', color='red', label='Total av')

    ax1.legend()

    ax1.set_ylabel('$z_{f}$ (m)')

    ax1.set_xlabel('n samples')

    plt.show()

    print('end')


def qh_vs_zf_hour_mean(all_days_vars_10minsa):
    """

    :return:
    """

    var_dict = all_days_vars_10minsa

    time = var_dict['time']

    z_f = var_dict['z_f']
    QH = var_dict['QH']

    df_dict = {'time': time, 'z_f': z_f, 'QH': QH}

    df = pd.DataFrame(df_dict)
    df = df.set_index('time')

    df = df.dropna()

    df.index = df.index.round('1s')

    ten_min = df.resample('10T', closed='right', label='right').mean()
    sixty_min = ten_min.resample('60T', closed='right', label='right').mean()

    df['z_f_hourly'] = sixty_min.z_f.reindex(df.index, method='bfill')
    df['QH_hourly'] = sixty_min.QH.reindex(df.index, method='bfill')

    fig, ax = plt.subplots(figsize=(7, 7))

    # identity line

    plt.plot(
        (df['z_f'] - df['z_f_hourly']) / df['z_f_hourly'],
        (df['z_f'] - df['z_f_hourly']) / df['z_f_hourly'],
        color='k', linewidth='0.5')

    plt.axhline(y=0, color='grey', linestyle=':', linewidth=0.5)
    plt.axvline(x=0, color='grey', linestyle=':', linewidth=0.5)

    s = ax.scatter(
        (df['z_f'] - df['z_f_hourly']) / df['z_f_hourly'],
        (df['QH'] - df['QH_hourly']) / df['QH_hourly'],
        marker='.', c=mdates.date2num(df.index))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    cbar = fig.colorbar(mappable=s, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(df.index[np.where(df.index.minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (H)')

    ax.set_ylabel('($Q_{H}^{i}$ - $\overline{Q_{H}^{hour}}$) / $\overline{Q_{H}^{hour}}$')

    ax.set_xlabel('($z_{f}^{i}$ - $z_{f}^{\overline{SA}, hour}$) / $z_{f}^{\overline{SA}, hour}$')

    plt.show()

    print('end')


def qh_vs_zf_day_mean(all_days_vars_10minsa):
    """

    :return:
    """

    var_dict = all_days_vars_10minsa

    time = var_dict['time']

    z_f = var_dict['z_f']
    QH = var_dict['QH']

    df_dict = {'time': time, 'z_f': z_f, 'QH': QH}

    df = pd.DataFrame(df_dict)
    df = df.set_index('time')

    df = df.dropna()

    df.index = df.index.round('1s')

    ten_min = df.resample('10T', closed='right', label='right').mean()

    # take mean of whole day
    day_mean_zf = np.mean(ten_min['z_f'])
    day_mean_qh = np.mean(ten_min['QH'])

    fig, ax = plt.subplots(figsize=(7, 7))

    # identity line
    plt.plot(
        (df['z_f'] - day_mean_zf) / day_mean_zf,
        (df['z_f'] - day_mean_zf) / day_mean_zf,
        color='k', linewidth='0.5')

    plt.axhline(y=0, color='grey', linestyle=':', linewidth=0.5)
    plt.axvline(x=0, color='grey', linestyle=':', linewidth=0.5)

    s = ax.scatter(
        (df['z_f'] - day_mean_zf) / day_mean_zf,
        (df['QH'] - day_mean_qh) / day_mean_qh,
        marker='.', c=mdates.date2num(df.index))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    cbar = fig.colorbar(mappable=s, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(df.index[np.where(df.index.minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (H)')

    ax.set_ylabel('($Q_{H}^{i}$ - $\overline{Q_{H}^{day}}$) / $\overline{Q_{H}^{day}}$')

    ax.set_xlabel('($z_{f}^{i}$ - $z_{f}^{\overline{SA}, day}$) / $z_{f}^{\overline{SA}, day}$')

    plt.show()

    print('end')


def qh_vs_zf_day_mean_both_days(all_days_vars_10minsa, all_days_vars_10minsa_142):
    """

    :return:
    """

    var_dict = all_days_vars_10minsa
    time = var_dict['time']
    z_f = var_dict['z_f']
    QH = var_dict['QH']
    kdown = var_dict['kdown']
    df_dict = {'time': time, 'z_f': z_f, 'QH': QH, 'kdown': kdown}
    df = pd.DataFrame(df_dict)
    df = df.set_index('time')
    df = df.dropna()
    df.index = df.index.round('1s')

    var_dict_142 = all_days_vars_10minsa_142
    time_142 = var_dict_142['time']
    z_f_142 = var_dict_142['z_f']
    QH_142 = var_dict_142['QH']
    kdown_142 = var_dict_142['kdown']
    df_dict_142 = {'time': time_142, 'z_f': z_f_142, 'QH': QH_142, 'kdown': kdown_142}
    df_142 = pd.DataFrame(df_dict_142)
    df_142 = df_142.set_index('time')
    df_142 = df_142.dropna()
    df_142.index = df_142.index.round('1s')
    # ten_min_142 = df_142.resample('10T', closed='right', label='right').mean()

    df.columns = ['z_f_111', 'QH_111', 'kdown_111']
    df_142.columns = ['z_f_142', 'QH_142', 'kdown_142']

    format_index_142 = df_142.index.strftime('%H:%M')
    format_index_111 = df.index.strftime('%H:%M')

    index_list_142 = []
    # construct datetime obj for both days with same year day etc. (for colourbar)
    for i in format_index_142:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_142.append(datetime_object)
    index_list_111 = []
    for i in format_index_111:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_111.append(datetime_object)

    df_142.index = index_list_142
    df.index = index_list_111

    combine_df = pd.concat([df_142, df], axis=1)
    combine_df = combine_df.dropna()

    # take mean of whole day
    day_mean_zf = np.mean(combine_df['z_f_111'])
    day_mean_qh = np.mean(combine_df['QH_111'])
    day_mean_zf_142 = np.mean(combine_df['z_f_142'])
    day_mean_qh_142 = np.mean(combine_df['QH_142'])

    fig, ax = plt.subplots(figsize=(7, 7))

    # identity line
    # plt.plot(
    #     (combine_df['z_f_111'] - day_mean_zf) / day_mean_zf,
    #     (combine_df['z_f_111'] - day_mean_zf) / day_mean_zf,
    #     color='k', linewidth='0.5')

    plt.axhline(y=0, color='grey', linestyle=':', linewidth=0.5)
    plt.axvline(x=0, color='grey', linestyle=':', linewidth=0.5)

    # 111
    bellow_50_111_index = np.where(combine_df.QH_111 < 50)[0]
    circ_111 = ax.scatter(
        (combine_df['z_f_111'][bellow_50_111_index] - day_mean_zf) / day_mean_zf,
        ((combine_df['QH_111'][bellow_50_111_index] - day_mean_qh) / day_mean_qh) / combine_df['kdown_111'][
            bellow_50_111_index],
        marker='o', facecolors='none', s=80, edgecolors='k', alpha=0.5)

    # 142
    bellow_50_142_index = np.where(combine_df.QH_142 < 50)[0]
    circ_142 = ax.scatter(
        (combine_df['z_f_142'][bellow_50_142_index] - day_mean_zf_142) / day_mean_zf_142,
        ((combine_df['QH_142'][bellow_50_142_index] - day_mean_qh_142) / day_mean_qh_142) / combine_df['kdown_142'][
            bellow_50_142_index],
        marker='o', facecolors='none', s=80, edgecolors='k', alpha=0.5, label='$Q_{H}^{i}$ < 50 $W$ $m^{-2}$')

    s = ax.scatter(
        (combine_df['z_f_111'] - day_mean_zf) / day_mean_zf,
        ((combine_df['QH_111'] - day_mean_qh) / day_mean_qh) / combine_df['kdown_111'],
        marker='+', c=mdates.date2num(combine_df.index), label='126', cmap=plt.cm.rainbow, s=20)

    s2 = ax.scatter(
        (combine_df['z_f_142'] - day_mean_zf_142) / day_mean_zf_142,
        ((combine_df['QH_142'] - day_mean_qh_142) / day_mean_qh_142) / combine_df['kdown_142'],
        marker='x', c=mdates.date2num(combine_df.index), label='123', cmap=plt.cm.rainbow, s=20)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    cbar = fig.colorbar(mappable=s, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(combine_df.index[np.where(combine_df.index.minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (H)')

    ax.set_ylabel(r'$\dfrac{(Q_{H}^{i} - \overline{Q_{H}^{day}}) / \overline{Q_{H}^{day}}}{k_{\downarrow}^{i}}$')

    ax.set_xlabel('($z_{f}^{i}$ - $z_{f}^{\overline{SA}, day}$) / $z_{f}^{\overline{SA}, day}$')

    ax.set_ylim(-0.022, 0.01)

    ax.legend(frameon=False)

    # plt.show()

    plt.savefig('C:/Users/beths/Desktop/LANDING/pls.png', bbox_inches='tight')

    print('end')
