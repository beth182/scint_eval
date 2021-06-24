import datetime as dt
import numpy as np
import ephem


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


def calculate_time(date, lat, lon, whatdoyouwant, utc_time):
    """
    a function to calculate times of sunrise or sunset or noon for a given day and location.

    :param date: datetime object of the time to convert to decimal time.
    :param lat: latitude of the location for which the times are being calculated.
    :param lon: longitude of the location for which the times are being calculated.
    :param whatdoyouwant: tell the function what you want to caclulate. 3 options:
    0 = time of sunrise.
    1 = time of sunset.
    2 = time of noon.
    :param utc_time: how many hours to add on to convert to UTC time.

    :return forreturn: time in decimal time.
    """
    # strip the datetime object
    datestripped = date.strftime("%Y/%m/%d 00:00:00")

    # Use lat and lon to create ephem observer instance and update with given
    # values
    my_location = ephem.Observer()
    my_location.lat = str(lat)
    my_location.lon = str(lon)
    my_location.date = datestripped

    # Get sunrise of the current day
    sunrise = my_location.next_rising(ephem.Sun())
    sunset = my_location.next_setting(ephem.Sun())
    noon = my_location.next_transit(ephem.Sun())

    # choices of what you want to calculate
    if whatdoyouwant == 0:
        # sunrise
        forreturn = ephem.Date(sunrise + utc_time * ephem.hour).datetime()
    if whatdoyouwant == 1:
        # sunset
        forreturn = ephem.Date(sunset + utc_time * ephem.hour).datetime()
    if whatdoyouwant == 2:
        # 'transit' -- i.e noon, for us normal speaking people
        forreturn = ephem.Date(noon + utc_time * ephem.hour).datetime()

    return forreturn
