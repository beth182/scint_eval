# B. Saunders 25/06/21
# Functions to reteive arrays from model eval scrips

import numpy as np


def retrive_arrays_obs(included_obs):
    """

    :return:
    """

    times = []
    vals = []

    stringtime = included_obs[1]
    stringtemp = included_obs[2]
    obvstimedict = included_obs[3]
    obvstempdict = included_obs[4]

    for day in stringtemp:
        for val in obvstempdict[day]:
            vals.append(val)

    for day in stringtime:
        for time in obvstimedict[day]:
            times.append(time)

    vals_array = np.asarray(vals)
    times_array = np.asarray(times)

    return times_array, vals_array


def retrive_arrays_model(included_models, model_grid_choice):

    try:
        included_model = included_models[model_grid_choice]

        stringtime = included_model[0]
        stringtemp = included_model[1]
        timedict = included_model[2]
        tempdict = included_model[3]

    except KeyError:
        print('No source area included in grid %d' % model_grid_choice)

        stringtime = []
        stringtemp = []
        timedict = []
        tempdict = []

    times = []
    vals = []

    for day in stringtemp:
        for val in tempdict[day]:
            vals.append(val)

    for day in stringtime:
        for time in timedict[day]:
            times.append(time)

    vals_array = np.asarray(vals)
    times_array = np.asarray(times)

    return times_array, vals_array


def rm_nans(times, vals):
    index_nans = np.argwhere(np.isnan(vals))

    vals_rm_nans = np.delete(vals, index_nans)
    times_rm_nans = np.delete(times, index_nans)

    return times_rm_nans, vals_rm_nans


def take_common_times(time_a, vals_a, time_b, vals_b):
    index_a = np.in1d(time_a, time_b)
    time_a_common = time_a[index_a]
    vals_a_common = vals_a[index_a]

    index_b = np.in1d(time_b, time_a_common)
    time_b_common = time_b[index_b]
    vals_b_common = vals_b[index_b]

    # sanity check that times are now the same
    assert time_a_common.all() == time_b_common.all()

    return time_a_common, vals_a_common, vals_b_common
