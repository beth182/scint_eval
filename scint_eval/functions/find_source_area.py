# B. Saunders 23/06/21
# function to find file path to raster with source area
import datetime


def find_source_area(time,
                     in_dir='C:/Users/beths/Desktop/LANDING/fp_output/hourly/',
                     name_start='BCT_IMU_15000_'):
    """

    :return:
    """

    sa_paths = []

    for hour in time:
        # find path
        sa_path = in_dir + name_start + hour.strftime('%Y') + '_' + hour.strftime('%j') + '_' + hour.strftime('%H') + '_' + hour.strftime('%M') + '.tif'
        sa_paths.append(sa_path)

    return sa_paths
