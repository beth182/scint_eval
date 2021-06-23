# B. Saunders 23/06/21
# function to find file path to raster with source area


def find_source_area(time,
                     in_dir = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/hourly/applicable_hours/',
                     name_start = 'BCT_IMU_65000_2016_142_'):
    """

    :return:
    """

    sa_paths = []

    for hour in time:
        # find path
        sa_path = in_dir + name_start + hour.strftime('%H') + '.tif'
        sa_paths.append(sa_path)

    return sa_paths



















    print('end')