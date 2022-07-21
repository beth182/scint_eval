import os.path
import datetime as dt
import sys
from calendar import isleap

from scint_eval import look_up


# ----------------------------------------------------------------------------------------------------------------------
def finding_files(file_format,
                  what_am_i_finding,
                  DOYstart,
                  DOYstop,
                  sitechoice,
                  run,
                  instrument,
                  sample,
                  variable,
                  obs_level,
                  model_path="/storage/basic/micromet/Tier_processing/rv006011/new_data_storage/",
                  obs_path="/storage/basic/micromet/Tier_raw/data/"
                  # obs_path="/storage/basic/micromet/Tier_processing/rv006011/new_L2_tests/"
                  ):
    """
    Reads in files.
    :param systemchoice: Determines what system the code is being run on, so save paths and data finding can change
    as appropriate. Currently can be laptop (ran on laptop or desktop), cluster (ran on met cluster) or newformat (for
    testing the MO new file format).
    This is entered as a string.
    :param DOYstart: date choices, where DOY is day of year. Start of date range.
    This is to be entered as a normal number, i.e. do not wrap
    one didget DOYs with 0's (example: DOY one is 1, and not 001).
    :param DOYstop: date choices, where DOY is day of year. End of date range. (Also, see above for DOYstart format).
    :param sitechoice: Choice of site.
    This is entered as a string.


    :return files_to_return: 3 dictionaries of filepaths of data to be read in. Observations, London model and the ukv.
    From the functions findfiles (for the cluster), and findfilesold (for laptop/desktop).
    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Finding files: ', what_am_i_finding, ' of the variable: ', variable)
    print(' ')

    if file_format == 'old':
        # old file format files (all stash codes in one file)
        # calls the findfiles function
        files_to_return = findfiles('/storage/basic/micromet/Tier_raw/data/',
                                    '/storage/basic/micromet/Tier_raw/data/',
                                    what_am_i_finding,
                                    sitechoice,
                                    DOYstart,
                                    DOYstop,
                                    run,
                                    instrument,
                                    sample,
                                    'old',
                                    variable,
                                    obs_level)

    elif file_format == 'new':
        # new file format files (individual stash codes)
        # calls the findfiles function
        files_to_return = findfiles(model_path,
                                    obs_path,
                                    what_am_i_finding,
                                    sitechoice,
                                    DOYstart,
                                    DOYstop,
                                    run,
                                    instrument,
                                    sample,
                                    'new',
                                    variable,
                                    obs_level)

    else:
        print('file_format choice: ', file_format, ' is not an option.')
        sys.exit()

    return files_to_return


def order_model_stashes(model,
                        files,
                        variable):
    """
    Sorts model files after they've been found - needs to be done as some variables require more than one stash code.
    Also needs to be done for variables with one stash code - as file paths are produced as lists from the other
    finding files function at the moment. This in the future could be moved to the other function (like how the obs
    have been handled).
    :param files:
    :param variable:
    :return:
    """
    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Ordering Model files: ', model)
    print(' ')

    # finds the stash code of the variable I am looking at
    stash = look_up.variables[variable]
    # if there is more than one stash code involved in this variable:
    if type(stash) == list:
        print('Variable: ', variable, ' uses more than one stash code.')

        if variable == 'RH_q':
            RH_stash = look_up.variables[variable]
            T_stash = RH_stash[0]
            P_stash = RH_stash[1]
            Q_stash = RH_stash[2]

            new_ukv_T = {}
            new_ukv_P = {}
            new_ukv_Q = {}

            # T
            for key in files.keys():
                for item in files[key]:
                    if T_stash in item:
                        new_ukv_T[key] = item
            # P
            for key in files.keys():
                for item in files[key]:
                    if P_stash in item:
                        new_ukv_P[key] = item
            # Q
            for key in files.keys():
                for item in files[key]:
                    if Q_stash in item:
                        new_ukv_Q[key] = item

            list_to_return = [new_ukv_T, new_ukv_P, new_ukv_Q]
            return list_to_return

        elif variable == 'wind':
            wind_stash = look_up.variables[variable]
            u_stash = wind_stash[0]
            v_stash = wind_stash[1]

            new_ukv_u = {}
            new_ukv_v = {}

            # u
            for key in files.keys():
                for item in files[key]:
                    if u_stash in item:
                        new_ukv_u[key] = item
            # v
            for key in files.keys():
                for item in files[key]:
                    if v_stash in item:
                        new_ukv_v[key] = item

            list_to_return = [new_ukv_u, new_ukv_v]
            return list_to_return

        elif variable == 'kup':
            up_stash = look_up.variables[variable]
            down_stash = up_stash[0]
            star_stash = up_stash[1]

            new_ukv_down = {}
            new_ukv_star = {}

            for key in files.keys():
                for item in files[key]:
                    if down_stash in item:
                        new_ukv_down[key] = item

            for key in files.keys():
                for item in files[key]:
                    if star_stash in item:
                        new_ukv_star[key] = item

            # making sure both stash codes needed have the same amount of files
            for down_item in new_ukv_down.keys():
                if down_item in new_ukv_star:
                    pass
                else:
                    del new_ukv_down[down_item]
            for star_item in new_ukv_star.keys():
                if star_item in new_ukv_down:
                    pass
                else:
                    del new_ukv_star[star_item]
            # Test if the keys are now the same
            if sorted(new_ukv_star.keys()) == sorted(new_ukv_down.keys()):
                if len(new_ukv_down) == len(new_ukv_star):
                    pass
            else:
                print("ERROR: The keys between both stash codes are different")
                sys.exit()

            list_to_return = [new_ukv_down, new_ukv_star]
            return list_to_return




    # for variables which only use one stash code:
    else:
        # define a dictionary
        new_model = {}
        for key in files.keys():
            for item in files[key]:
                if stash in item:
                    new_model[key] = item
        return new_model


# ----------------------------------------------------------------------------------------------------------------------
# Finding files
def findfiles(modpath,
              obvspath,
              what_am_i_finding,
              sitechoice,
              DOYstart,
              DOYstop,
              run,
              instrument,
              sample,
              MO_format,
              variable,
              obs_level):
    """
    Finds files. Called from the finding_files function (which is called by main) bellow.
    :param modpath:
    :param obvspath:
    :param what_am_i_finding: tells the function what type of files you are wanting to find - observations? Model?
    if model, what model? Fed as string. at the moment, can be 'obs', 'ukv', 'lon'
    :param sitechoice:
    :param DOYstart:
    :param DOYstop:
    :param run: what model run: should be a string, '06Z' or '21Z'.
    :param instrument: Instrument used for taking the obs. This is in a dictionary within variables.py
    :param sample: Sample of the obs. example: '15min' - has to be a string
    :param MO_format:
    :param variable:
    :return:
    """

    # ------------------------------------------------------------------------------------------------------------------
    # finding start and stop years, and start and stop DOYs
    # (has been re-done to include the option to run more than one year at once)
    # makes into string
    strDOYstart = str(DOYstart)
    strDOYstop = str(DOYstop)
    # splits sting, year (first 4 digits of string):
    start_year = strDOYstart[:4]
    stop_year = strDOYstop[:4]
    # DOY (last 3 digits of string)
    start_DOY = strDOYstart[4:]
    stop_DOY = strDOYstop[4:]

    # finding number of years we are dealing with:
    num_of_years = int(stop_year) - int(start_year) + 1  # the + 1 is included to represent the actual number of years
    # creates a list for all years included
    year_list = []
    if num_of_years == 1:
        year_list.append(start_year)
    elif num_of_years == 2:
        year_list.append(start_year)
        year_list.append(stop_year)
    else:
        for i in range(0, num_of_years):
            year_to_append = int(start_year) + i
            year_list.append(str(year_to_append))

    # DOY dictionary (used to be list) for all DOYs in between start and stop (the ones we want), for each year included
    DOYlist = {}
    # creates each year included as a key
    for item in year_list:
        DOYlist[item] = []

    # fills dictionary based on DOYs available in that year
    # wraps the string to be zero padded.
    # if only 1 year is avalible
    if num_of_years == 1:
        for item in range(int(start_DOY), int(stop_DOY) + 1):
            if item < 10:
                DOYlist[start_year].append('00' + str(item))
            if item < 100:
                if item > 9:
                    DOYlist[start_year].append('0' + str(item))
            else:
                DOYlist[start_year].append(str(item))

    # if 2 years are chosen
    elif num_of_years >= 2:
        # is the first year a leap year?
        if isleap(int(start_year)):
            whole_year = 367
        else:
            whole_year = 366
        # fills the first year
        for item in range(int(start_DOY), whole_year):
            if item < 10:
                DOYlist[start_year].append('00' + str(item))
            if item < 100:
                if item > 9:
                    DOYlist[start_year].append('0' + str(item))
            else:
                DOYlist[start_year].append(str(item))
        # fills the last year
        for item in range(1, int(stop_DOY) + 1):
            if item < 10:
                DOYlist[stop_year].append('00' + str(item))
            if item < 100:
                if item > 9:
                    DOYlist[stop_year].append('0' + str(item))
            else:
                DOYlist[stop_year].append(str(item))
        # fills any years in-between (if there are any)
        if num_of_years > 2:
            for year in year_list[1:-1]:
                # is this year a leap year?
                if isleap(int(year)):
                    whole_year = 367
                else:
                    whole_year = 366
                # fills the year
                for item in range(1, whole_year):
                    if item < 10:
                        DOYlist[year].append('00' + str(item))
                    if item < 100:
                        if item > 9:
                            DOYlist[year].append('0' + str(item))
                    else:
                        DOYlist[year].append(str(item))

    # prints out DOYs chosen in terminal
    print('DOYs chosen:')
    for key in sorted(DOYlist.keys()):
        print('year:', key)
        print(DOYlist[key])

    # if only looking at one day, the DOY before the chosen day is also added (as the model files begin at 6 am, and I
    # need midnight to midnight.

    # if num_of_years == 1:
    #     if len(DOYlist[start_year]) == 1:
    #         day_before = int(start_DOY) - 1
    #         if day_before < 10:
    #             DOYlist[start_year].append('00' + str(day_before))
    #         if day_before < 100:
    #             if day_before > 9:
    #                 DOYlist[start_year].append('0' + str(day_before))
    #         else:
    #             DOYlist[start_year].append(str(day_before))

    # ------------------------------------------------------------------------------------------------------------------
    # FINDING OBSERVATIONS
    # ------------------------------------------------------------------------------------------------------------------
    if what_am_i_finding == 'obs':
        # creates dictionary to append observations to
        obvsdict = {}

        # finding observations year by year.
        for year in year_list:
            print(' ')
            print('For year: ', year)
            obvsmainpath = obvspath + year + '/London/' + obs_level + '/' + sitechoice + '/DAY'
            # list of all DOY folders in the observation site folder

            try:
                DOYoptions = os.listdir(obvsmainpath)
            except OSError:
                print(' ')
                print('OBS FOR THIS YEAR DO NOT EXIST')
                continue

            # List of all matches between available DOYs and wanted DOYs
            DOYmatches = []
            for item in DOYoptions:
                if item in DOYlist[year]:
                    DOYmatches.append(item)

            # Double checking all DOYs have been found
            obvsmissingDOY = []
            # printing any missing DOYs
            if len(DOYmatches) == len(DOYlist[year]):
                print('All obvs DOYs found')
            else:
                print('There is a missing DOY/DOYs:')
                for item in DOYlist[year]:
                    if item in DOYmatches:
                        pass
                    else:
                        print(item)
                        obvsmissingDOY.append(item)

            # finding files
            # list for all files which should exists (that should be in DOYmatches)
            obvsfilepaths = []
            for item in DOYmatches:
                pathto = obvsmainpath + '/' + item + '/'
                # example file formats
                # Davis_BFCL_2017254_15min.nc
                # CNR1_IMU_2018012_15min.nc
                # stripping the date and constructing a date object in the same format as the file name (based on above)
                dateobject = dt.datetime.strptime(str(year) + ' ' + item, '%Y %j')
                # constructing filename
                filename = instrument + '_' + sitechoice + '_' + str(year) + dateobject.strftime(
                    '%j') + '_' + sample + '.nc'
                path = pathto + filename
                obvsfilepaths.append(path)

            # finding what files do exist and what files don't exist based on what should exist
            obvsexistlist = []
            obvsdontexistlist = []
            for item in obvsfilepaths:
                if os.path.exists(item) == True:
                    obvsexistlist.append(item)
                else:
                    obvsdontexistlist.append(item)

            # printing what doesn't exist
            if len(obvsexistlist) == len(DOYlist[year]):
                print('all ' + str(len(DOYlist[year])) + ' obs files found')
            else:
                print('obs: ' + str(len(obvsexistlist)) + ' out of ' + str(
                    len(DOYlist[year])) + ' files found. Missing:')
                obvsmissinglist = obvsmissingDOY + obvsdontexistlist
                print(obvsmissinglist)

            # Adding these files to the observation dictionary
            if MO_format == 'old':
                startstepobvs = 0
                for item in obvsexistlist:
                    stingname = 'obs' + year + str(startstepobvs)
                    obvsdict[stingname] = item
                    startstepobvs += 1

            elif MO_format == 'new':
                obsDOYs = []
                for item in obvsexistlist:
                    DOY = item.split('_')[-2][-3:]
                    obsDOYs.append(DOY)
                # Making a list of the index where the DOY changes
                doychangeobs = []
                for i in range(1, len(obsDOYs)):
                    if obsDOYs[i - 1] == obsDOYs[i]:
                        pass
                    else:
                        doychangeobs.append(i)
                if len(doychangeobs) == 0:
                    if len(obsDOYs) == 0:
                        print(' no obs!')
                    else:
                        obslistdoy0 = obsDOYs
                        obslist0 = obvsexistlist
                        obvsdict['obs' + year + str(obslistdoy0[0])] = obslist0
                else:
                    # Creating a dictionary for the values of each DOY
                    # first item
                    obslistdoy0 = obsDOYs[0:doychangeobs[0]]
                    obslist0 = obvsexistlist[0:doychangeobs[0]]
                    obvsdict['obs' + year + str(obslistdoy0[0])] = obslist0
                    # middle items
                    obsi = 1
                    for item in range(1, len(doychangeobs)):
                        listdoy = obsDOYs[doychangeobs[obsi - 1]:doychangeobs[obsi]]
                        list = obvsexistlist[doychangeobs[obsi - 1]:doychangeobs[obsi]]
                        obvsdict['obs' + year + str(listdoy[0])] = list
                        obsi += 1
                    # final item
                    obslistdoyend = obsDOYs[doychangeobs[-1]:len(obsDOYs)]
                    obslistend = obvsexistlist[doychangeobs[-1]:len(obvsexistlist)]
                    obvsdict['obs' + year + str(obslistdoyend[0])] = obslistend

            else:
                print('MO_format choice not an option.')
                sys.exit()

        # prepares files to be used
        new_obvs = {}
        for key in obvsdict.keys():
            for item in obvsdict[key]:
                new_obvs[key] = item

        print(' ')
        return new_obvs

    # ------------------------------------------------------------------------------------------------------------------
    # MODEL THINGS
    # ------------------------------------------------------------------------------------------------------------------
    # If what_am_i_finding is part of the model dict invariables.py:
    if what_am_i_finding in look_up.model_options.keys():
        # creates dictionaries to append model files to
        ukvdict = {}

        # finding model files year by year.
        for year in year_list:
            print(' ')
            print('For year: ', year)
            # finding all model DOYs which exists
            modmainpath = modpath + year + '/London/L2/MetOffice/DAY'
            DOYoptionsmod = os.listdir(modmainpath)
            # List of all matches between avalible DOYs and wanted DOYs
            DOYmatchesmod = []
            for item in DOYoptionsmod:
                if item in DOYlist[year]:
                    DOYmatchesmod.append(item)
            modmissingDOY = []
            if len(DOYmatchesmod) == len(DOYlist[year]):
                print('All model DOYs found')
            else:
                print('There is a missing DOY/DOYs for the model:')
                for item in DOYlist[year]:
                    if item in DOYmatchesmod:
                        pass
                    else:
                        print(item)
                        modmissingDOY.append(item)

            ############################################################################################################
            # comments/ steps taken are similar as above for the observations
            ukvfilepaths = []
            for item in DOYmatchesmod:
                if MO_format == 'old':
                    # example file name
                    # MOUKV_FC2017102706Z_DAVIS_BCT.nc
                    # MOLON_FC2017102706Z_DAVIS_BCT.nc
                    dateobject = dt.datetime.strptime(str(year) + ' ' + item, '%Y %j')

                    # where model_options[what_am_i_finding][0] is the model filename preface
                    filename = look_up.model_options[what_am_i_finding][0] + dateobject.strftime('%Y%m%d') + run + '_' + \
                               look_up.sites[
                                   sitechoice] + '.nc'

                    pathto = modmainpath + '/' + item + '/'
                    path = pathto + filename
                    ukvfilepaths.append(path)

                elif MO_format == 'new':
                    # (Changed to see if I can get more relevant missing files to work)
                    if variable == 'wind' or variable == 'RH_q' or variable == 'kup':
                        # requires more than one stash code.
                        codes = look_up.variables[variable]
                        dateobject = dt.datetime.strptime(str(year) + ' ' + item, '%Y %j')
                        for code in codes:
                            # where model_options[what_am_i_finding][0] is the model filename preface
                            filename = look_up.model_options[what_am_i_finding][0] + dateobject.strftime(
                                '%Y%m%d') + run + '_' + code + '_' + look_up.sites[
                                           sitechoice] + '.nc'

                            pathto = modmainpath + '/' + item + '/'
                            path = pathto + filename
                            ukvfilepaths.append(path)

                    else:
                        # requires only one stash code
                        code = look_up.variables[variable]
                        dateobject = dt.datetime.strptime(str(year) + ' ' + item, '%Y %j')

                        # where model_options[what_am_i_finding][0] is the model filename preface
                        filename = look_up.model_options[what_am_i_finding][0] + dateobject.strftime(
                            '%Y%m%d') + run + '_' + code + '_' + look_up.sites[
                                       sitechoice] + '.nc'

                        pathto = modmainpath + '/' + item + '/'
                        path = pathto + filename
                        ukvfilepaths.append(path)
                else:
                    print('MO_format not an option.')
                    sys.exit()

            if MO_format == 'old':
                ukvexistlist = []
                ukvdontexistlist = []
                for item in ukvfilepaths:
                    if os.path.exists(item) == True:
                        ukvexistlist.append(item)
                    else:
                        ukvdontexistlist.append(item)

                if len(ukvexistlist) == len(DOYlist[year]):
                    print('all ' + str(len(DOYlist[year])) + ' ' + what_am_i_finding + ' files found')
                else:
                    print(what_am_i_finding + ': ' + str(len(ukvexistlist)) + ' out of ' + str(
                        len(DOYlist[year])) + ' files found. Missing:')
                    ukvmissinglist = modmissingDOY + ukvdontexistlist
                    print(ukvmissinglist)

                startstepukv = 0
                for item in ukvexistlist:
                    stingname = what_am_i_finding + year + str(startstepukv)
                    ukvdict[stingname] = item
                    startstepukv += 1

            elif MO_format == 'new':
                # Changed to see if I can get more relevant missing files to work
                ukvexist = 0
                ukvexistlist = []
                ukvdontexistlist = []
                for item in ukvfilepaths:
                    if os.path.exists(item) == True:
                        ukvexist += 1
                        ukvexistlist.append(item)
                    else:
                        ukvdontexistlist.append(item)

                if len(ukvdontexistlist) == 0:
                    print('all ' + str(len(ukvexistlist)) + ' files exist from ' + str(len(DOYlist[year])) + ' DOYs')
                else:
                    totalleng = len(ukvexistlist) + len(ukvdontexistlist)
                    print(str(ukvexist) + ' out of ' + str(totalleng) + ' files found. Missing:')
                    ukvmissinglist = modmissingDOY + ukvdontexistlist
                    print(ukvmissinglist)

                ukvDOYs = []
                for item in ukvexistlist:

                    # KSSW is a site with more letters than others, so it's handled differently when finding the date:
                    if sitechoice == 'KSSW':
                        strip = item[-34:-26]
                    elif sitechoice == 'BFCL':
                        strip = item[-34:-26]
                    elif sitechoice == 'MR':
                        strip = item[-32:-24]
                    elif sitechoice == 'NK':
                        strip = item[-32:-24]
                    else:
                        strip = item[-33:-25]
                    time = dt.datetime.strptime(strip, '%Y%m%d')
                    DOY = time.strftime('%j')
                    ukvDOYs.append(DOY)

                # Making a list of the index where the DOY changes
                doychangeukv = []
                for i in range(1, len(ukvDOYs)):
                    if ukvDOYs[i - 1] == ukvDOYs[i]:
                        pass
                    else:
                        doychangeukv.append(i)

                if len(doychangeukv) == 0:
                    if len(ukvDOYs) == 0:
                        print('No files for: ' + what_am_i_finding)
                    else:
                        ukvlistdoy0 = ukvDOYs
                        ukvlist0 = ukvexistlist
                        ukvdict[what_am_i_finding + year + str(ukvlistdoy0[0])] = ukvlist0

                else:
                    # Creating a dictionary for the values of each DOY
                    # first item
                    ukvlistdoy0 = ukvDOYs[0:doychangeukv[0]]
                    ukvlist0 = ukvexistlist[0:doychangeukv[0]]
                    ukvdict[what_am_i_finding + year + str(ukvlistdoy0[0])] = ukvlist0

                    # middle items
                    ukvi = 1
                    for item in range(1, len(doychangeukv)):
                        listdoy = ukvDOYs[doychangeukv[ukvi - 1]:doychangeukv[ukvi]]
                        list = ukvexistlist[doychangeukv[ukvi - 1]:doychangeukv[ukvi]]
                        ukvdict[what_am_i_finding + year + str(listdoy[0])] = list
                        ukvi += 1

                    # final item
                    ukvlistdoyend = ukvDOYs[doychangeukv[-1]:len(ukvDOYs)]
                    ukvlistend = ukvexistlist[doychangeukv[-1]:len(ukvexistlist)]
                    ukvdict[what_am_i_finding + year + str(ukvlistdoyend[0])] = ukvlistend

            else:
                print('MO_format not an option.')
                sys.exit()

        print(' ')
        return ukvdict
