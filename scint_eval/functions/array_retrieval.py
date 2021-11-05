# B. Saunders 25/06/21
# Functions to reteive arrays from model eval scrips

import numpy as np
import datetime as dt
import pandas as pd


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
            # round time to the nearest minute
            rounded_time = roundTime(time)

            times.append(rounded_time)

    vals_array = np.asarray(vals)
    times_array = np.asarray(times)

    return times_array, vals_array

def roundTime(dt_ob=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt_ob == None : dt_ob = dt_ob.datetime.now()
   seconds = (dt_ob.replace(tzinfo=None) - dt_ob.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt_ob + dt.timedelta(0,rounding-seconds,-dt_ob.microsecond)

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


def time_average_values(vals, time, minute_resolution):
    """
    Time average a variable
    :param vals:
    :param time:
    :param minute_resolution: int of number of minutes to average to
    :return:
    """

    # put the data into a pandas dataframe

    df_dict = {'time': time, 'vals': vals}

    df = pd.DataFrame(df_dict)

    # construct a string to go into resample denoting the rule
    freq_string = str(minute_resolution) + 'T'

    # resample to minute_resolution
    resample_df = df.resample(freq_string, on='time', closed='right', label='right').mean()

    resample_df = resample_df.reset_index()

    return np.asarray(resample_df['time'].to_list()), np.asarray(resample_df['vals'].to_list())
