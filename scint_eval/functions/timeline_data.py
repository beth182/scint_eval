import datetime as dt
import os
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import scintools as sct

# Beth Saunders 12/05/2022
# file to look at avail files for scintillometer paths


# path 11 - BTT -> BCT


def retrieve_all_days(DOYstart, DOYstop):
    """
    Gets all days between start and stop as a list of datetime objects
    :return:
    """

    # convert the DOYstart and stop into datetime objects
    dt_start = dt.datetime.strptime(str(DOYstart), "%Y%j")
    dt_stop = dt.datetime.strptime(str(DOYstop), "%Y%j")

    # calculate difference between these two dates
    delta = dt_stop - dt_start

    # define a list of days in between start and stop
    days_list = []
    for i in range(delta.days + 1):
        day = dt_start + dt.timedelta(days=i)
        days_list.append(day)

    return days_list


def construct_file_path(days_list,
                        main_path,
                        level,
                        rx_site,
                        instrument,
                        sample
                        ):
    """
    construct a file path for each of the days between start and stop
    :param days_list:
    :return:
    """

    file_paths = []
    for day in days_list:
        year = day.strftime('%Y')
        DOY = day.strftime('%j')

        # /storage/basic/micromet/Tier_raw/data/2018/London/L1/IMU/DAY/001
        dir_path = main_path + year + '/London/' + level + '/' + rx_site + '/DAY/' + DOY + '/'

        # LASMkII_Fast_IMU_2016001_15min.nc
        file_name = instrument + '_' + rx_site + '_' + year + DOY + '_' + sample + '.nc'

        file_path = dir_path + file_name

        file_paths.append(file_path)

    return file_paths


def retrieve_data_avail(file_paths):
    """
    list to append a nan (file doesnt exist or all day's data are nan), or 1 (some data is present for the day)
    :return:
    """

    file_exists_list = []

    for file_path in file_paths:

        if os.path.exists(file_path):

            # open file
            print(file_path)
            nc_file = nc.Dataset(file_path)
            QH = nc_file.variables['Q_H']

            # convert to array
            qh_array = np.array(QH)

            # test if all vals are missing
            if np.all((qh_array == -999.)):
                file_exists_list.append(np.nan)
            else:
                file_exists_list.append(1)


        else:
            file_exists_list.append(np.nan)

    return file_exists_list


def plot_data_avail(days_list,
                    file_exists_list11,
                    file_exists_list12,
                    file_exists_list13,
                    file_exists_list14,
                    file_exists_list15):
    """
    Plot of data avilability for the scintilloemetr paths
    :param file_exists_list:
    :return:
    """

    plt.figure(figsize=(13, 4))
    ax = plt.subplot(1, 1, 1)

    # define seasons start and stop
    DJF_16_start = dt.datetime.strptime('2016 01 01', "%Y %m %d")
    DJF_16_stop = dt.datetime.strptime('2016 03 01', "%Y %m %d")
    MAM_16_start = dt.datetime.strptime('2016 03 01', "%Y %m %d")
    MAM_16_stop = dt.datetime.strptime('2016 06 01', "%Y %m %d")
    JJA_16_start = dt.datetime.strptime('2016 06 01', "%Y %m %d")
    JJA_16_stop = dt.datetime.strptime('2016 09 01', "%Y %m %d")
    SON_16_start = dt.datetime.strptime('2016 09 01', "%Y %m %d")
    SON_16_stop = dt.datetime.strptime('2016 12 01', "%Y %m %d")


    DJF_17_start = dt.datetime.strptime('2016 12 01', "%Y %m %d")
    DJF_17_stop = dt.datetime.strptime('2017 03 01', "%Y %m %d")
    MAM_17_start = dt.datetime.strptime('2017 03 01', "%Y %m %d")
    MAM_17_stop = dt.datetime.strptime('2017 06 01', "%Y %m %d")
    JJA_17_start = dt.datetime.strptime('2017 06 01', "%Y %m %d")
    JJA_17_stop = dt.datetime.strptime('2017 09 01', "%Y %m %d")
    SON_17_start = dt.datetime.strptime('2017 09 01', "%Y %m %d")
    SON_17_stop = dt.datetime.strptime('2017 12 01', "%Y %m %d")

    DJF_18_start = dt.datetime.strptime('2017 12 01', "%Y %m %d")
    DJF_18_stop = dt.datetime.strptime('2018 03 01', "%Y %m %d")
    MAM_18_start = dt.datetime.strptime('2018 03 01', "%Y %m %d")
    MAM_18_stop = dt.datetime.strptime('2018 06 01', "%Y %m %d")
    JJA_18_start = dt.datetime.strptime('2018 06 01', "%Y %m %d")
    JJA_18_stop = dt.datetime.strptime('2018 09 01', "%Y %m %d")
    SON_18_start = dt.datetime.strptime('2018 09 01', "%Y %m %d")
    SON_18_stop = dt.datetime.strptime('2018 12 01', "%Y %m %d")

    DJF_19_start = dt.datetime.strptime('2018 12 01', "%Y %m %d")
    DJF_19_stop = dt.datetime.strptime('2019 03 01', "%Y %m %d")

    ax.axvspan(DJF_16_start, DJF_16_stop, alpha=0.3, color='lightblue')
    ax.axvspan(DJF_17_start, DJF_17_stop, alpha=0.3, color='lightblue')
    ax.axvspan(DJF_18_start, DJF_18_stop, alpha=0.3, color='lightblue')
    ax.axvspan(DJF_19_start, DJF_19_stop, alpha=0.3, color='lightblue')

    ax.axvspan(MAM_16_start, MAM_16_stop, alpha=0.3, color='thistle')
    ax.axvspan(MAM_17_start, MAM_17_stop, alpha=0.3, color='thistle')
    ax.axvspan(MAM_18_start, MAM_18_stop, alpha=0.3, color='thistle')

    ax.axvspan(JJA_16_start, JJA_16_stop, alpha=0.3, color='palegoldenrod')
    ax.axvspan(JJA_17_start, JJA_17_stop, alpha=0.3, color='palegoldenrod')
    ax.axvspan(JJA_18_start, JJA_18_stop, alpha=0.3, color='palegoldenrod')

    ax.axvspan(SON_16_start, SON_16_stop, alpha=0.3, color='indianred')
    ax.axvspan(SON_17_start, SON_17_stop, alpha=0.3, color='indianred')
    ax.axvspan(SON_18_start, SON_18_stop, alpha=0.3, color='indianred')



    plt.plot(days_list, np.array(file_exists_list11) * 11, linewidth=5, color='blue')
    plt.plot(days_list, np.array(file_exists_list12) * 12, linewidth=5, color='red')
    plt.plot(days_list, np.array(file_exists_list13) * 13, linewidth=5, color='green')
    plt.plot(days_list, np.array(file_exists_list14) * 14, linewidth=5, color='orange')
    plt.plot(days_list, np.array(file_exists_list15) * 15, linewidth=5, color='magenta')

    plt.xlim(days_list[0], days_list[-1])

    plt.ylim(10, 16)

    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_formatter(DateFormatter('%Y%j'))

    plt.show()


# define inputs
# DOYstarti = 2016001
# DOYstopi = 2018366

# Autumn 2017
DOYstarti = 2017060
DOYstopi = 2017151

main_pathi = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/'
leveli = 'L1'
samplei = '15min'

# path 11 - BTT -> BCT
path_11 = sct.ScintillometerPair(x=[282251.14, 285440.6056],
                                 y=[5712486.47, 5712253.017],
                                 z_asl=[180, 142],
                                 pair_id='BTT_BCT',
                                 crs='epsg:32631')

# path 12 - BCT -> IMU
path_12 = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                 y=[5712253.017, 5712935.032],
                                 z_asl=[142, 88],
                                 pair_id='BCT_IMU',
                                 crs='epsg:32631')

# path 13 - IMU -> BTT
path_13 = sct.ScintillometerPair(x=[284562.3107, 282251.14],
                                 y=[5712935.032, 5712486.47],
                                 z_asl=[88, 180],
                                 pair_id='IMU_BTT',
                                 crs='epsg:32631')

# path 14 - IMU -> SWT
path_14 = sct.ScintillometerPair(x=[284562.3107, 285407],
                                 y=[5712935.032, 5708599.83],
                                 z_asl=[88, 44],
                                 pair_id='IMU_SWT',
                                 crs='epsg:32631')

# path 15 - SCT -> SWT
path_15 = sct.ScintillometerPair(x=[284450.1944, 285407],
                                 y=[5708094.734, 5708599.83],
                                 z_asl=[51, 44],
                                 pair_id='SCT_SWT',
                                 crs='epsg:32631')

days_list = retrieve_all_days(DOYstarti, DOYstopi)

# get the RX site for the path
rx_site11 = path_11.pair_id.split('_')[1]
rx_site12 = path_12.pair_id.split('_')[1]
rx_site13 = path_13.pair_id.split('_')[1]
rx_site14 = path_14.pair_id.split('_')[1]
rx_site15 = path_15.pair_id.split('_')[1]

file_paths11 = construct_file_path(days_list,
                                   main_pathi,
                                   leveli,
                                   rx_site11,
                                   'LASMkII_Fast',
                                   samplei)

file_paths12 = construct_file_path(days_list,
                                   main_pathi,
                                   leveli,
                                   rx_site12,
                                   'LASMkII_Fast',
                                   samplei)

file_paths13 = construct_file_path(days_list,
                                   main_pathi,
                                   leveli,
                                   rx_site13,
                                   'BLS',
                                   samplei)

file_paths14 = construct_file_path(days_list,
                                   main_pathi,
                                   leveli,
                                   rx_site14,
                                   'BLS',
                                   samplei)
file_paths15 = construct_file_path(days_list,
                                   main_pathi,
                                   leveli,
                                   rx_site15,
                                   'LASMkII_Fast',
                                   samplei)

file_exists_list11 = retrieve_data_avail(file_paths11)
file_exists_list12 = retrieve_data_avail(file_paths12)
file_exists_list13 = retrieve_data_avail(file_paths13)
file_exists_list14 = retrieve_data_avail(file_paths14)
file_exists_list15 = retrieve_data_avail(file_paths15)



plot_data_avail(days_list,
                file_exists_list11,
                file_exists_list12,
                file_exists_list13,
                file_exists_list14,
                file_exists_list15)

print('end')
