# quick look at nc files

import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import cm
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import math

from scint_eval.functions import ukv_landuse

mpl.rcParams.update({'font.size': 15})


def df_from_nc_and_csv(nc_path_123, nc_path_126,
                       csv_path_123, csv_path_126):
    """
    Take nc file (with QH, kdown, time) and csv file (with lc fractions) - and combine the two together
    :return:
    """

    # read in files
    nc_123 = nc.Dataset(nc_path_123)
    nc_126 = nc.Dataset(nc_path_126)

    # read csv files
    df_123 = pd.read_csv(csv_path_123)
    df_126 = pd.read_csv(csv_path_126)

    # read time
    file_time_123 = nc_123.variables['time']
    file_time_126 = nc_126.variables['time']

    time_dt_123 = nc.num2date(file_time_123[:], file_time_123.units)
    time_dt_126 = nc.num2date(file_time_126[:], file_time_126.units)

    QH_123 = nc_123.variables['QH'][:]
    QH_126 = nc_126.variables['QH'][:]

    kdown_123 = nc_123.variables['kdown'][:]
    kdown_126 = nc_126.variables['kdown'][:]

    nc_df_dict_123 = {'time': time_dt_123, 'QH': QH_123, 'kdown': kdown_123}
    nc_df_dict_126 = {'time': time_dt_126, 'QH': QH_126, 'kdown': kdown_126}

    nc_df_123 = pd.DataFrame(nc_df_dict_123)
    nc_df_126 = pd.DataFrame(nc_df_dict_126)

    nc_df_123 = nc_df_123.set_index('time')
    nc_df_126 = nc_df_126.set_index('time')

    nc_df_123.index = nc_df_123.index.round('1s')
    nc_df_126.index = nc_df_126.index.round('1s')

    nc_df_123['QH_norm'] = QH_123 / kdown_123
    nc_df_126['QH_norm'] = QH_126 / kdown_126

    df_123.index = df_123['Unnamed: 0']
    df_123 = df_123.drop('Unnamed: 0', 1)

    df_126.index = df_126['Unnamed: 0']
    df_126 = df_126.drop('Unnamed: 0', 1)

    df_123.index = pd.to_datetime(df_123.index, format='%d/%m/%Y %H:%M')
    df_126.index = pd.to_datetime(df_126.index, format='%Y-%m-%d %H:%M:%S')

    minutes = 10
    freq_string = str(minutes) + 'Min'

    group_times_123 = df_123.groupby(pd.Grouper(freq=freq_string, label='left')).first()
    group_times_126 = df_126.groupby(pd.Grouper(freq=freq_string, label='left')).first()

    outputs_df_123 = pd.DataFrame({'Building': [], 'Impervious': [], 'Water': [], 'Grass': [],
                                   'Deciduous': [], 'Evergreen': [], 'Shrub': []})

    outputs_df_126 = pd.DataFrame({'Building': [], 'Impervious': [], 'Water': [], 'Grass': [],
                                   'Deciduous': [], 'Evergreen': [], 'Shrub': []})

    for i, row in group_times_123.iterrows():
        time = i

        # time_array = np.array([time + dt.timedelta(minutes=i) for i in range(minutes)])
        time_array = np.array(
            [(time + dt.timedelta(minutes=1) - dt.timedelta(minutes=minutes)) + dt.timedelta(minutes=i) for i in
             range(minutes)])

        Building = df_123['Building'][np.where(df_123.index == time)[0]]
        Impervious = df_123['Impervious'][np.where(df_123.index == time)[0]]
        Water = df_123['Water'][np.where(df_123.index == time)[0]]
        Grass = df_123['Grass'][np.where(df_123.index == time)[0]]
        Deciduous = df_123['Deciduous'][np.where(df_123.index == time)[0]]
        Evergreen = df_123['Evergreen'][np.where(df_123.index == time)[0]]
        Shrub = df_123['Shrub'][np.where(df_123.index == time)[0]]

        df_dict = {'time': time_array}

        lc_types = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

        for lc_type in lc_types:

            lc_type_series = df_123[lc_type][np.where(df_123.index == time)[0]]

            if len(lc_type_series) == 0:
                nan_series = pd.Series([np.nan])
                lc_type_series = lc_type_series.append(nan_series)
            else:
                if type(lc_type_series.values[0]) == str:
                    lc_type_series.values[0] = 0

            try:
                df_dict[lc_type] = np.ones(len(time_array)) * lc_type_series.values[0]
            except:
                print('end')

        period_df = pd.DataFrame(df_dict)
        period_df = period_df.set_index('time')

        outputs_df_123 = outputs_df_123.append(period_df)

    for i, row in group_times_126.iterrows():
        time = i

        # time_array = np.array([time + dt.timedelta(minutes=i) for i in range(minutes)])
        time_array = np.array(
            [(time + dt.timedelta(minutes=1) - dt.timedelta(minutes=minutes)) + dt.timedelta(minutes=i) for i in
             range(minutes)])

        Building = df_126['Building'][np.where(df_126.index == time)[0]]
        Impervious = df_126['Impervious'][np.where(df_126.index == time)[0]]
        Water = df_126['Water'][np.where(df_126.index == time)[0]]
        Grass = df_126['Grass'][np.where(df_126.index == time)[0]]
        Deciduous = df_126['Deciduous'][np.where(df_126.index == time)[0]]
        Evergreen = df_126['Evergreen'][np.where(df_126.index == time)[0]]
        Shrub = df_126['Shrub'][np.where(df_126.index == time)[0]]

        df_dict = {'time': time_array}

        lc_types = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

        for lc_type in lc_types:

            lc_type_series = df_126[lc_type][np.where(df_126.index == time)[0]]

            if len(lc_type_series) == 0:
                nan_series = pd.Series([np.nan])
                lc_type_series = lc_type_series.append(nan_series)
            else:
                if type(lc_type_series.values[0]) == str:
                    lc_type_series.values[0] = 0

            try:
                df_dict[lc_type] = np.ones(len(time_array)) * lc_type_series.values[0]
            except:
                print('end')

        period_df = pd.DataFrame(df_dict)
        period_df = period_df.set_index('time')

        outputs_df_126 = outputs_df_126.append(period_df)

    outputs_df_123['sum'] = outputs_df_123.sum(axis=1)
    outputs_df_126['sum'] = outputs_df_126.sum(axis=1)

    outputs_df_123['Urban'] = outputs_df_123['Building'] + outputs_df_123['Impervious']
    outputs_df_126['Urban'] = outputs_df_126['Building'] + outputs_df_126['Impervious']

    df_123 = nc_df_123.merge(outputs_df_123, how='inner', left_index=True, right_index=True)
    df_126 = nc_df_126.merge(outputs_df_126, how='inner', left_index=True, right_index=True)

    return {'123': df_123, '126': df_126}


def stats_of_extent(nc_path_123, nc_path_126):
    """
    Get stats of SA extent from nc file
    :return:
    """

    # read in files
    nc_123 = nc.Dataset(nc_path_123)
    nc_126 = nc.Dataset(nc_path_126)

    # read time
    file_time_123 = nc_123.variables['time']
    file_time_126 = nc_126.variables['time']

    time_dt_123 = nc.num2date(file_time_123[:], file_time_123.units)
    time_dt_126 = nc.num2date(file_time_126[:], file_time_126.units)

    extent_123 = nc_123.variables['sa_area_km2'][:]
    extent_126 = nc_126.variables['sa_area_km2'][:]

    # get max vals
    max_extent_123 = np.nanmax(extent_123)
    max_extent_126 = np.nanmax(extent_126)

    min_extent_123 = np.nanmin(extent_123)
    min_extent_126 = np.nanmin(extent_126)

    max_extent_time_123 = time_dt_123[np.where(extent_123 == max_extent_123)[0]]
    max_extent_time_126 = time_dt_126[np.where(extent_126 == max_extent_126)[0]]

    min_extent_time_123 = time_dt_123[np.where(extent_123 == min_extent_123)[0]]
    min_extent_time_126 = time_dt_126[np.where(extent_126 == min_extent_126)[0]]

    av_123 = np.nanmean(extent_123)
    av_126 = np.nanmean(extent_126)

    print('end')


def stats_of_water(csv_path_123, csv_path_126):
    """
    Get stats of water fraction
    :return:
    """

    # read csv files
    df_123 = pd.read_csv(csv_path_123)
    df_126 = pd.read_csv(csv_path_126)

    df_123.index = df_123['Unnamed: 0']
    df_123 = df_123.drop('Unnamed: 0', 1)

    df_126.index = df_126['Unnamed: 0']
    df_126 = df_126.drop('Unnamed: 0', 1)

    df_123.index = pd.to_datetime(df_123.index, format='%d/%m/%Y %H:%M')
    df_126.index = pd.to_datetime(df_126.index, format='%Y-%m-%d %H:%M:%S')

    max_water_123 = np.nanmax(df_123['Water'])
    max_water_time = df_123.iloc[np.where(df_123['Water'] == max_water_123)[0]].index

    print('end')


def stats_of_the_fluxes(df_dict):
    """
    Get stats of the fluxes
    :return:
    """

    df_123 = df_dict['123']
    df_126 = df_dict['126']

    df_123 = df_123.dropna()
    df_126 = df_126.dropna()

    df_123_std = df_123.resample('10T', closed='right', label='right').std()
    df_126_std = df_126.resample('10T', closed='right', label='right').std()

    max_val_123 = df_123_std.QH.max()
    max_val_123_time = df_123_std.index[np.where(df_123_std.QH == max_val_123)[0]]

    max_val_126 = df_126_std.QH.max()
    max_val_126_time = df_126_std.index[np.where(df_126_std.QH == max_val_126)[0]]

    min_val_123 = df_123_std.QH.min()
    min_val_123_time = df_123_std.index[np.where(df_123_std.QH == min_val_123)[0]]

    min_val_126 = df_126_std.QH.min()
    min_val_126_time = df_126_std.index[np.where(df_126_std.QH == min_val_126)[0]]

    mean_std_126 = df_126_std.QH.mean()
    mean_std_123 = df_123_std.QH.mean()

    print('end')


def times_series_line_QH_KDOWN(df):
    """
    TIME SERIES OF Q AND KDOWN LINE PLOT
    :return:
    """

    fig = plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)

    ax.plot(df['QH'], label='$Q_{H}$', linewidth=1)
    ax.plot(df['kdown'], label='$K_{\downarrow}$', linewidth=1)

    ax.set_xlabel('Time (hh:mm)')
    ax.set_ylabel('Flux (W $m^{-2}$)')

    ax.set_xlim(df.index[0] - dt.timedelta(minutes=10), df.index[-1] + dt.timedelta(minutes=10))
    ax.set_ylim(0, 1000)

    plt.legend()

    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    plt.title('DOY: ' + df.index[0].strftime('%j'))

    plt.show()

    print('end')


def urb_frac_vs_QH_norm_time(df_dict):
    """
    Urban faction (x) vs. QH normalised by kdown (y) with the colourbar as time
    :return:
    """

    df_123 = df_dict['123']
    df_126 = df_dict['126']

    fig, ax = plt.subplots(figsize=(10, 10))
    cmap = cm.get_cmap('plasma')

    # construct datetime obj for both days with same year day etc. (for colourbar)
    format_index_123 = df_123.index.strftime('%H:%M')
    format_index_126 = df_126.index.strftime('%H:%M')

    index_list_123 = []
    for i in format_index_123:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_123.append(datetime_object)

    index_list_126 = []
    for i in format_index_126:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_126.append(datetime_object)

    df_123.index = index_list_123
    df_126.index = index_list_126

    df_123_select = df_123[['kdown', 'Urban', 'QH_norm']]
    df_123_select.rename({'kdown': 'kdown_123', 'Urban': 'Urban_123', 'QH_norm': 'QH_norm_123'}, axis=1, inplace=True)

    df_126_select = df_126[['kdown', 'Urban', 'QH_norm']]
    df_126_select.rename({'kdown': 'kdown_126', 'Urban': 'Urban_126', 'QH_norm': 'QH_norm_126'}, axis=1, inplace=True)

    combine_df = pd.concat([df_123_select, df_126_select], axis=1)

    print('end')

    start_dt = dt.datetime(combine_df.index[0].year, combine_df.index[0].month, combine_df.index[0].day, 10)
    end_dt = dt.datetime(combine_df.index[0].year, combine_df.index[0].month, combine_df.index[0].day, 14)
    where_index = np.where((combine_df.index >= start_dt) & (combine_df.index <= end_dt))[0]

    s_123 = ax.scatter(combine_df['Urban_123'][where_index], combine_df['QH_norm_123'][where_index],
                       c=mdates.date2num(combine_df.index)[where_index], marker='x', cmap=cmap, edgecolor='None',
                       label='123')

    s_126 = ax.scatter(combine_df['Urban_126'][where_index], combine_df['QH_norm_126'][where_index],
                       c=mdates.date2num(combine_df.index)[where_index], marker='o', cmap=cmap, edgecolor='None',
                       label='126')

    plt.legend()

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    cbar = fig.colorbar(mappable=s_123, cax=cax, orientation="vertical")

    cbar.set_ticks(mdates.date2num(combine_df.index[where_index][np.where(combine_df.index[where_index].minute == 0)]))

    cbar.ax.set_yticklabels(
        [mdates.num2date(i).strftime('%H') for i in cbar.get_ticks()])  # set ticks of your format
    cbar.set_label('Time (h)')

    ax.set_xlabel('Built Fraction (%)')
    ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')

    plt.show()

    print('end')


def urb_frac_vs_QH_norm_kdown(df_dict, mod_time_123, mod_vals_123, mod_time_126, mod_vals_126, lc_df_123, lc_df_126):
    """
    Urban faction (x) vs. QH normalised by kdown (y) with the colourbar as kdown
    :return:
    """

    # get model kdown for both days
    mod_kdown_time_123, mod_kdown_vals_123 = ukv_landuse.get_ukv_KSSW_kdown(2016122)
    mod_kdown_time_126, mod_kdown_vals_126 = ukv_landuse.get_ukv_KSSW_kdown(2016125)

    # combine model results into a dataframe

    mod_dict_kdown_123 = {'time': mod_kdown_time_123, 'kdown': mod_kdown_vals_123}
    mod_kdown_df_123 = pd.DataFrame.from_dict(mod_dict_kdown_123)
    mod_kdown_df_123 = mod_kdown_df_123.set_index('time')

    mod_dict_kdown_126 = {'time': mod_kdown_time_126, 'kdown': mod_kdown_vals_126}
    mod_kdown_df_126 = pd.DataFrame.from_dict(mod_dict_kdown_126)
    mod_kdown_df_126 = mod_kdown_df_126.set_index('time')

    mod_dict_QH_123 = {'time': mod_time_123, 'QH': mod_vals_123}
    mod_QH_df_123 = pd.DataFrame.from_dict(mod_dict_QH_123)
    mod_QH_df_123 = mod_QH_df_123.set_index('time')

    mod_dict_QH_126 = {'time': mod_time_126, 'QH': mod_vals_126}
    mod_QH_df_126 = pd.DataFrame.from_dict(mod_dict_QH_126)
    mod_QH_df_126 = mod_QH_df_126.set_index('time')

    mod_df_123 = pd.concat([mod_kdown_df_123, mod_QH_df_123], axis=1)
    mod_df_126 = pd.concat([mod_kdown_df_126, mod_QH_df_126], axis=1)

    mod_df_123 = mod_df_123.dropna()
    mod_df_126 = mod_df_126.dropna()

    lc_df_123.index = pd.to_datetime(lc_df_123.index, format='%y%m%d%H')
    lc_df_126.index = pd.to_datetime(lc_df_126.index, format='%y%m%d%H')

    lc_df_123['Urban'] = lc_df_123['roof'] + lc_df_123['canyon']
    lc_df_126['Urban'] = lc_df_126['roof'] + lc_df_126['canyon']

    # swap for build fraction vs building fraction
    # mod_df_123['Urban'] = lc_df_123['Urban']
    # mod_df_126['Urban'] = lc_df_126['Urban']
    mod_df_123['Urban'] = lc_df_123['roof']
    mod_df_126['Urban'] = lc_df_126['roof']


    # fig, ax = plt.subplots(figsize=(10, 10))
    #
    # cmap = cm.get_cmap('rainbow')
    #
    # smallest_kdown = min(mod_df_123.kdown.min(), mod_df_126.kdown.min())
    # largest_kdown = max(mod_df_123.kdown.max(), mod_df_126.kdown.max())
    #
    # bounds = np.linspace(smallest_kdown, largest_kdown, len(mod_df_126) + 1)
    # norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    #
    # s123 = ax.scatter(mod_df_123.Urban * 100, mod_df_123.QH / mod_df_123.kdown, c=mod_df_123.kdown, marker='x', cmap=cmap, norm=norm,
    #                    edgecolor='None', label='Cloudy')
    #
    # s126 = ax.scatter(mod_df_126.Urban * 100, mod_df_126.QH / mod_df_126.kdown, c=mod_df_126.kdown, marker='o', cmap=cmap, norm=norm,
    #                    edgecolor='None', label='Clear')
    #
    # plt.legend()
    #
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes("right", size="5%", pad=0.1)
    # cbar = fig.colorbar(mappable=s123, cax=cax, orientation="vertical")
    # cax.set_ylabel('$K_{\downarrow}$', rotation=270, labelpad=20)
    #
    # ax.set_xlabel('Built Fraction (%)')
    # ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')
    #
    # plt.show()


    df_123 = df_dict['123']
    df_126 = df_dict['126']

    # construct datetime obj for both days with same year day etc. (for colourbar)
    format_index_123 = df_123.index.strftime('%H:%M')
    format_index_126 = df_126.index.strftime('%H:%M')

    index_list_123 = []
    for i in format_index_123:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_123.append(datetime_object)

    index_list_126 = []
    for i in format_index_126:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_126.append(datetime_object)

    df_123.index = index_list_123
    df_126.index = index_list_126
    # swap for build vs building fractions
    # df_123_select = df_123[['kdown', 'Urban', 'QH_norm']]
    # df_123_select.rename({'kdown': 'kdown_123', 'Urban': 'Urban_123', 'QH_norm': 'QH_norm_123'}, axis=1,
    #                      inplace=True)
    #
    # df_126_select = df_126[['kdown', 'Urban', 'QH_norm']]
    # df_126_select.rename({'kdown': 'kdown_126', 'Urban': 'Urban_126', 'QH_norm': 'QH_norm_126'}, axis=1,
    #                      inplace=True)


    df_123_select = df_123[['kdown', 'Building', 'QH_norm']]
    df_123_select.rename({'kdown': 'kdown_123', 'Building': 'Urban_123', 'QH_norm': 'QH_norm_123'}, axis=1,
                         inplace=True)

    df_126_select = df_126[['kdown', 'Building', 'QH_norm']]
    df_126_select.rename({'kdown': 'kdown_126', 'Building': 'Urban_126', 'QH_norm': 'QH_norm_126'}, axis=1,
                         inplace=True)

    combine_df = pd.concat([df_123_select, df_126_select], axis=1)

    time_grouper = pd.Grouper(freq='10T', closed='left', label='left', offset='1min')
    time_groups = combine_df.groupby(time_grouper)

    start_times_126 = []
    x_vals_126 = []
    y_vals_126 = []
    IQR25_vals_126 = []
    IQR75_vals_126 = []
    mean_kdown_126 = []

    for start_time, time_group in time_groups:

        time_group['x_axis_vals'] = time_group['Urban_126']
        x_axis_vals = time_group['x_axis_vals']

        # check that all 10 min fraction vals in the column are the same
        if len(x_axis_vals) == 0:
            continue
        elif x_axis_vals.isnull().all():
            continue
        else:
            assert (x_axis_vals[0] == x_axis_vals).all()

        x_axis_val = x_axis_vals[0]

        time_group['y_axis_vals'] = time_group['QH_norm_126']
        y_axis_vals = time_group['y_axis_vals']

        median = y_axis_vals.median()

        IQR_25 = y_axis_vals.quantile(.25)
        IQR_75 = y_axis_vals.quantile(.75)

        mean_kdown = np.nanmean(time_group['kdown_126'])

        start_times_126.append(start_time)
        x_vals_126.append(x_axis_val)
        y_vals_126.append(median)
        IQR25_vals_126.append(IQR_25)
        IQR75_vals_126.append(IQR_75)
        mean_kdown_126.append(mean_kdown)

    start_times_123 = []
    x_vals_123 = []
    y_vals_123 = []
    IQR25_vals_123 = []
    IQR75_vals_123 = []
    mean_kdown_123 = []

    for start_time, time_group in time_groups:

        time_group['x_axis_vals'] = time_group['Urban_123']
        x_axis_vals = time_group['x_axis_vals']

        # check that all 10 min fraction vals in the column are the same
        if len(x_axis_vals) == 0:
            continue
        elif x_axis_vals.isnull().all():
            continue
        else:
            assert (x_axis_vals[0] == x_axis_vals).all()

        x_axis_val = x_axis_vals[0]

        time_group['y_axis_vals'] = time_group['QH_norm_123']
        y_axis_vals = time_group['y_axis_vals']

        median = y_axis_vals.median()

        IQR_25 = y_axis_vals.quantile(.25)
        IQR_75 = y_axis_vals.quantile(.75)

        mean_kdown = np.nanmean(time_group['kdown_123'])

        start_times_123.append(start_time)
        x_vals_123.append(x_axis_val)
        y_vals_123.append(median)
        IQR25_vals_123.append(IQR_25)
        IQR75_vals_123.append(IQR_75)
        mean_kdown_123.append(mean_kdown)

    start_dt = dt.datetime(combine_df.index[0].year, combine_df.index[0].month, combine_df.index[0].day, 10)
    end_dt = dt.datetime(combine_df.index[0].year, combine_df.index[0].month, combine_df.index[0].day, 14)

    start_times_123 = np.asarray(start_times_123)
    start_times_126 = np.asarray(start_times_126)

    where_index_123 = np.where((start_times_123 >= start_dt) & (start_times_123 <= end_dt))[0]
    where_index_126 = np.where((start_times_126 >= start_dt) & (start_times_126 <= end_dt))[0]

    where_index_mod_123 = np.where((mod_df_123.index.hour >= start_dt.hour) & (mod_df_123.index.hour <= end_dt.hour))[0]
    where_index_mod_126 = np.where((mod_df_126.index.hour >= start_dt.hour) & (mod_df_126.index.hour <= end_dt.hour))[0]
    mod_select_126 = mod_df_126.iloc[where_index_mod_126]
    mod_select_123 = mod_df_123.iloc[where_index_mod_123]

    start_times_123_select = np.asarray(start_times_123)[where_index_123]
    start_times_126_select = np.asarray(start_times_126)[where_index_126]

    x_vals_123_select = np.asarray(x_vals_123)[where_index_123]
    y_vals_123_select = np.asarray(y_vals_123)[where_index_123]

    x_vals_126_select = np.asarray(x_vals_126)[where_index_126]
    y_vals_126_select = np.asarray(y_vals_126)[where_index_126]

    IQR25_vals_123_select = np.asarray(IQR25_vals_123)[where_index_123]
    IQR25_vals_126_select = np.asarray(IQR25_vals_126)[where_index_126]

    IQR75_vals_123_select = np.asarray(IQR75_vals_123)[where_index_123]
    IQR75_vals_126_select = np.asarray(IQR75_vals_126)[where_index_126]

    mean_kdown_123_select = np.asarray(mean_kdown_123)[where_index_123]
    mean_kdown_126_select = np.asarray(mean_kdown_126)[where_index_126]





    fig, ax = plt.subplots(figsize=(10, 10))
    cmap = cm.get_cmap('rainbow')

    smallest_kdown = min(min(mean_kdown_123_select), min(mean_kdown_123_select), mod_select_123.kdown.min(), mod_select_126.kdown.min())
    largest_kdown = max(max(mean_kdown_126_select), max(mean_kdown_126_select), mod_select_123.kdown.max(), mod_select_126.kdown.max())

    bounds = np.linspace(smallest_kdown, largest_kdown, len(start_times_123_select) + 1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    smap = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    list_of_rgba_123 = smap.to_rgba(mean_kdown_123_select)
    list_of_rgba_126 = smap.to_rgba(mean_kdown_126_select)

    for i in range(0, len(mean_kdown_123_select)):
        ax.vlines(x_vals_123_select[i], IQR25_vals_123_select[i], IQR75_vals_123_select[i], color=list_of_rgba_123[i])

    for i in range(0, len(mean_kdown_126_select)):
        ax.vlines(x_vals_126_select[i], IQR25_vals_126_select[i], IQR75_vals_126_select[i], color=list_of_rgba_126[i])

    s_123 = ax.scatter(x_vals_123_select, y_vals_123_select, c=mean_kdown_123_select, marker='x', cmap=cmap, norm=norm,
                       edgecolor='None', label='Cloudy')
    s_126 = ax.scatter(x_vals_126_select, y_vals_126_select, c=mean_kdown_126_select, marker='o', cmap=cmap, norm=norm,
                       edgecolor='None', label='Clear')


    ax.scatter(mod_select_126.Urban * 100, mod_select_126.QH / mod_select_126.kdown, c=mod_select_126.kdown, marker='^', cmap=cmap, norm=norm,
                       edgecolor='k', label='Clear UKV', s=80)
    ax.scatter(mod_select_123.Urban * 100, mod_select_123.QH / mod_select_123.kdown, c=mod_select_123.kdown, marker='s', cmap=cmap, norm=norm,
                       edgecolor='k', label='Cloudy UKV', s=80)


    plt.legend()

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = fig.colorbar(mappable=s_123, cax=cax, orientation="vertical")
    cax.set_ylabel('$K_{\downarrow}$', rotation=270, labelpad=20)

    ax.set_xlabel('Built Fraction (%)')
    ax.set_ylabel('$Q_{H}$ / $K_{\downarrow}$')



    # plt.show()



    plt.savefig('C:/Users/beths/Desktop/LANDING/yayeet.png', bbox_inches='tight')

    print('end')


def run_quick_look(mod_time_123, mod_vals_123, mod_time_126, mod_vals_126, lc_df_123, lc_df_126,
                   path_123='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/123/LASMkII_Fast_IMU_2016123_1min_sa10min.nc',
                   path_126='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/126/LASMkII_Fast_IMU_2016126_1min_sa10min.nc',
                   csv_123='C:/Users/beths/Desktop/LANDING/mask_tests/123_10_mins.csv',
                   csv_126='C:/Users/beths/Desktop/LANDING/mask_tests/126_10_mins.csv'):
    # test = stats_of_extent(path_123, path_126)
    # test = stats_of_water(csv_123, csv_126)
    df_dict = df_from_nc_and_csv(path_123, path_126, csv_123, csv_126)
    # test2 = stats_of_the_fluxes(df_dict)
    # times_series_line_QH_KDOWN(df_dict['126'])
    # urb_frac_vs_QH_norm_time(df_dict)
    urb_frac_vs_QH_norm_kdown(df_dict, mod_time_123, mod_vals_123, mod_time_126, mod_vals_126, lc_df_123, lc_df_126)
