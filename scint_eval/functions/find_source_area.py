# B. Saunders 23/06/21
# function to find file path to raster with source area

import numpy as np


def take_hourly_vars(time_dict,
                     string_time):
    """
    Takes dictionary of ncdf output and takes only values on the hour.
    :param var_dict: dictionary of ncdf output
    :return: dict of values on the hour
    """

    hourly_dict = {}

    for day in string_time:

        day_arr = np.asarray(time_dict[day])

        # index of where time is on the hour
        hour_index = np.where([i.minute == 0 for i in day_arr])
        hour_time = day_arr[hour_index]

        hourly_dict[day] = hour_time

    return hourly_dict


def find_source_area(time_dict,
                     string_time):
    """

    :return:
    """

    in_dir = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/hourly/applicable_hours/'
    name_start = 'BCT_IMU_65000_2016_142_'

    sa_dict = {}

    # list of hours with SA made
    sa_hours_avail = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    for day in string_time:

        sa_dict[day] = []

        for hour in time_dict[day]:
            if hour.hour in sa_hours_avail:

                # find path
                sa_path = in_dir + name_start + hour.strftime('%H') + '.tif'

                sa_dict[day].append(sa_path)

    return sa_dict



















    print('end')