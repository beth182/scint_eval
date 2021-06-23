# B. Saunders 23/06/21
# Take values on the hour only

# imports
import numpy as np


def take_hourly_vars(time,
                     vals):
    """
    takes only values on the hour.
    """

    # index of where time is on the hour
    hour_index = np.where([i.minute == 0 for i in np.asarray(time)])
    hour_time = np.asarray(time)[hour_index]
    hour_vals = np.asarray(vals)[hour_index]

    return hour_time, hour_vals


def dicts_to_lists(time_dict,
                   val_dict,
                   time_strings,
                   val_strings):
    """
    Takes 2 dicts and 2 lists of keys - and converts contents to 2 lists
    :return:
    """

    times_list = []
    vals_list = []

    for time_string in time_strings:
        for time in time_dict[time_string]:
            times_list.append(time)

    for val_string in val_strings:
        for val in val_dict[val_string]:
            vals_list.append(val)

    return times_list, vals_list
