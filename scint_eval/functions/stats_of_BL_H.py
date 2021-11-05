# Looks at different height levels of BL flux - and compares to surface

from itertools import islice
import netCDF4 as nc
import numpy as np
from scint_eval.functions import tools
import datetime as dt


def mbe(mod, obvs):
    differencesmbe = mod - obvs
    mbe_val = differencesmbe.mean()
    return mbe_val


def stats_BL_flux(files_ukv):
    """

    :return:
    """

    # read
    path = []
    for key, value in islice(files_ukv.items(), 0, None):
        path.append(value)
    path = path[0]
    ncfile = nc.Dataset(path)

    # heights
    heights = ncfile.variables['level_height']
    heights = heights[:]
    height_index = 3  # 60 m is 4th in list - so ind 3
    height = heights[height_index]

    # time
    time_units = ncfile.variables['time'].units
    time_ref = [np.squeeze(ncfile.variables['forecast_reference_time'])]
    time_ref_dt = tools.time_to_datetime(time_units, time_ref)[0]
    time_period = np.squeeze(ncfile.variables['forecast_period'][:])
    time_list = [time_ref_dt + dt.timedelta(seconds=hr * 3600) for hr in time_period]
    index_to_start = 3  # skip first 3 hours
    hours_to_stop = 24  # how many hours before getting into next day
    index_to_stop = index_to_start + hours_to_stop

    time_list = time_list[index_to_start:index_to_stop]

    # grid index
    # for grid E
    index_lat = 1
    index_lon = 1

    # read
    var = ncfile.variables['boundary_layer_heat_fluxes']
    # from surface
    var_surf = var[index_lat, index_lon, index_to_start:index_to_stop, 0]
    # from height
    var_height = var[index_lat, index_lon, index_to_start:index_to_stop, height_index]

    # calculate the mean bias error
    mbe_all = mbe(var_surf, var_height)

    diff = var_surf - var_height

    max_diff = np.max(diff)

    time_max_diff = time_list[np.where(diff == np.max(diff))[0][0]]














    print('end')