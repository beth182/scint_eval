# B. Saunders 23/06/21
# function to find file path to raster with source area
import datetime


def find_source_area(time,
                     in_dir='C:/Users/beths/Desktop/LANDING/fp_output/hourly/',
                     name_start='BCT_IMU_65000_'):
    """

    :return:
    """

    sa_paths = []

    for hour in time:
        # find path
        if hour != datetime.datetime(2016, 5, 22, 0, 0):
            sa_path = in_dir + name_start + '2016_142_' + hour.strftime('%H') + '.tif'
        else:
            sa_path = in_dir + name_start + '2016_143_' + hour.strftime('%H') + '.tif'

        sa_paths.append(sa_path)

    return sa_paths
