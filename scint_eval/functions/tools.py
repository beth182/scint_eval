import datetime as dt
import numpy as np


# Elliott's function to create datetime objects from the model
def time_to_datetime(tstr, timeRaw):
    """
    Convert 'time since:... and an array/list of times into a list of datetimes
    :param tstr: string along the lines of 'secs/mins/hours since ........'
    :param timeRaw:
    :return: list of processed times
    EW: 13/03/17
    """
    # sort out times and turn into datetimes
    # tstr = datafile.variables['time'].units
    tstr = tstr.replace('-', ' ')
    tstr = tstr.split(' ')
    # Datetime
    # ---------------
    # create list of datetimes for export
    # start date in netCDF file
    start = dt.datetime(int(tstr[2]), int(tstr[3]), int(tstr[4]))
    if tstr[0] == 'seconds':
        # get delta times from the start date
        # time: time in minutes since the start time (taken from netCDF file)
        delta = [dt.timedelta(seconds=int(timeRaw[i])) for i in range(0, len(timeRaw))]
    elif tstr[0] == 'minutes':
        delta = [dt.timedelta(seconds=int(timeRaw[i] * 60)) for i in range(0, len(timeRaw))]
    elif tstr[0] == 'hours':
        delta = [dt.timedelta(seconds=int(timeRaw[i] * 3600)) for i in range(0, len(timeRaw))]
    if 'delta' in locals():
        return [start + delta[i] for i in np.arange(0, len(timeRaw))]
    else:
        print('Raw time not in seconds, minutes or hours. No processed time created.')
        return
