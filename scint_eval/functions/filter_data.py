import math
import numpy as np


def remove_nans(stringtime,
                stringtemp,
                obvstimedict,
                obvstempdict,

                stringtemplon,
                lontempdict,

                stringtempukv,
                ukvtempdict,

                stringtimelon,
                lontimedict,

                stringtimeukv,
                ukvtimedict,

                hoursbeforerepeat=24):
    print(' ')
    print('------------------')
    print('Removing NaNs')

    # appending all to one list, in order, to work maths things on...
    # all obvs
    allobvsvalues = []
    allobvstimes = []

    for templist in stringtemp:
        currentlist = obvstempdict[templist]
        for temp in currentlist:
            allobvsvalues.append(temp)
    for timelist in stringtime:
        currentlist = obvstimedict[timelist]
        for time in currentlist:
            allobvstimes.append(time)
    # all lon model
    alllonvalues = []
    alllontimes = []
    for templist in stringtemplon:
        currentlist = lontempdict[templist][:hoursbeforerepeat]
        for temp in currentlist:
            alllonvalues.append(temp)

    for timelist in stringtimelon:
        currentlist = lontimedict[timelist]
        for time in currentlist:
            alllontimes.append(time)

    # all UKV model
    allukvvalues = []
    allukvtimes = []
    for templist in stringtempukv:
        currentlist = ukvtempdict[templist][:hoursbeforerepeat]
        for temp in currentlist:
            allukvvalues.append(temp)

    for timelist in stringtimeukv:
        currentlist = ukvtimedict[timelist]
        for time in currentlist:
            allukvtimes.append(time)

    # TURNING LISTS INTO ARRAYS
    obvarray = np.array(allobvsvalues)
    # finding any nans about in obvs, and saves their index
    nanplace = []
    for place, nan in enumerate(allobvsvalues):
        if math.isnan(nan):
            nanplace.append(place)
    print('there are: ', len(nanplace), ' number of NaNs')
    # np.where(np.isnan(obvarray)) might be a 1 line way to do this???
    lengthbefore = len(obvarray)
    print('lengh of times array before nans are removed:', lengthbefore)
    # remove nans from obvs
    obvarray = [value for value in obvarray if not math.isnan(value)]
    lengthafter = len(obvarray)
    print('lengh of times array after nans are removed:', lengthafter)

    times = np.array(allobvstimes)
    nanplace = np.array(nanplace)
    times = np.delete(times, nanplace)
    # turns times back to list
    times = times.tolist()

    # finding any nans about in model, and saves their index
    lonnanplace = []
    ukvnanplace = []
    for place, nan in enumerate(allukvvalues):
        if type(nan) is np.ma.core.MaskedConstant:
            ukvnanplace.append(place)
    print('there are: ', len(ukvnanplace), ' number of NaNs in the UKV model')
    for place, nan in enumerate(alllonvalues):
        if type(nan) is np.ma.core.MaskedConstant:
            lonnanplace.append(place)
    print('there are: ', len(lonnanplace), ' number of NaNs in the London model')
    # turning into array
    lonarray = np.array(alllonvalues)
    ukvarray = np.array(allukvvalues)

    lonlengthbefore = len(lonarray)
    print('lengh of times in the London model array before nans are removed:', lonlengthbefore)
    # remove nans from obvs
    lonarray = [value for value in lonarray if not math.isnan(value)]
    lonlengthafter = len(lonarray)
    print('lengh of times array after nans are removed:', lonlengthafter)
    print(' ')
    ukvlengthbefore = len(ukvarray)
    print('lengh of times in the UKV model array before nans are removed:', ukvlengthbefore)
    # remove nans from obvs
    ukvarray = [value for value in ukvarray if not math.isnan(value)]
    ukvlengthafter = len(ukvarray)
    print('lengh of times array after nans are removed:', ukvlengthafter)

    if len(lonnanplace) > 0:
        lontimes = np.array(alllontimes)
        # Remove nans from time
        lonnanplace = np.array(lonnanplace)
        lontimes = np.delete(lontimes, lonnanplace)
        # turns times back to list
        lontimes = lontimes.tolist()
    else:
        lontimes = alllontimes

    if len(ukvnanplace) > 0:

        ukvtimes = np.array(allukvtimes)
        # Remove nans from time
        ukvnanplace = np.array(ukvnanplace)
        ukvtimes = np.delete(ukvtimes, ukvnanplace)
        # turns times back to list
        ukvtimes = ukvtimes.tolist()
    else:
        ukvtimes = allukvtimes

    return (times,
            lontimes,
            ukvtimes,
            obvarray,
            lonarray,
            ukvarray)
