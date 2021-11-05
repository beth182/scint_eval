import numpy as np
import matplotlib as mpl
import pandas as pd
from datetime import datetime
import sys

from scint_eval.functions import file_read
from scint_eval.functions import sort_model
from scint_eval.functions import sa_grid_extraction
from scint_eval import look_up

# mpl.rcParams.update({'font.size': 20})  # updating the matplotlib fontsize


def prepare_model_grid_percentages(time, sa_list, savepath,
                                   csv_path='C:/Users/beths/Desktop/LANDING/ukv_grid_sa_percentages.csv'):
    """

    :return:
    """

    # reads the csv
    existing_df = pd.read_csv(csv_path)

    # defines dicts
    # will have hours as keys, and then list of grid numbers or grid percentages
    model_site_dict = {}
    percentage_vals_dict = {}
    percentage_covered_by_model = {}

    for hour, sa in zip(time, sa_list):

        time_key = hour.strftime("%y%m%d%H")

        # check to see if time is in csv
        if time_key in existing_df.hour.astype(str).str[0:8].tolist():

            # value exists: gets the values from the csv
            exists_index = np.where(np.asarray(existing_df.hour.astype(str).str[0:8].tolist()) == time_key)[0][0]

            df_row = existing_df.iloc[[exists_index]]

            # gets column names
            # [1:] gets rid of 'hour'
            no_zeros = df_row.loc[:, (df_row != 0).any(axis=0)]

            calculated_sum = no_zeros.values.tolist()[0][1]

            model_site = list(no_zeros.columns)[2:]
            percentage_vals = no_zeros.values.tolist()[0][2:]

            # append to dictionaries
            model_site_dict[time_key] = model_site
            percentage_vals_dict[time_key] = percentage_vals
            percentage_covered_by_model[time_key] = calculated_sum


        else:
            # gets the percentage values for each grid
            grid_vals, calculated_sum = sa_grid_extraction.SA_grid_percentages(sa, savepath, hour.strftime('%H'))

            # calculated sum is the % of the total footprint captured falling within the model grids

            # new dict for grids to be included
            included_grids_vals_raw = {}

            for grid in sorted(grid_vals):
                grid_val = grid_vals[grid]

                # if the percentage is larger than 1
                if grid_val > 0:
                    # append to dictionary
                    included_grids_vals_raw[grid] = grid_val

            # calculating a new percentage from a new 100% - as we have discared some of the percentages
            # (any grid bellow 1)
            new_100 = sum(included_grids_vals_raw.values())

            included_grids_vals = {}

            for grid in sorted(included_grids_vals_raw):
                grid_val = included_grids_vals_raw[grid]

                # calculates a new percentage value
                new_val = (grid_val / new_100) * 100

                included_grids_vals[grid] = new_val

            model_site = sorted(included_grids_vals.keys())

            # percentage vals
            percentage_vals = []
            for grid in model_site:
                per_val = included_grids_vals[grid]
                percentage_vals.append(per_val)

            # append to dictionaries
            model_site_dict[time_key] = model_site
            percentage_vals_dict[time_key] = percentage_vals
            percentage_covered_by_model[time_key] = calculated_sum

            # append to a csv - to cut-down on processing time
            append_grids_to_csv(time_key, model_site, percentage_vals, calculated_sum)

    return model_site_dict, percentage_vals_dict, percentage_covered_by_model


def append_grids_to_csv(time_key, model_site, percentage_vals, calculated_sum,
                        csv_path='C:/Users/beths/Desktop/LANDING/ukv_grid_sa_percentages.csv'):
    """
    function to append to a csv - to cut-down on processing time
    :return:
    """

    # reads the csv
    existing_df = pd.read_csv(csv_path)

    # creates array of 0's with the same length as time, calculated_sum, then number of grids (42) - total = 44
    zeros_array = np.zeros(44)

    # first value in array is the time
    zeros_array[0] = int(time_key)

    # second is calculated sum
    zeros_array[1] = calculated_sum

    for grid, percent in zip(model_site, percentage_vals):
        # get the index of where the percentage is going to go in the dataframe
        # this would normally be - take away 1 from the grid (grid 1 - 42 = index 0 - 41)
        # but as I have time as my first index, then WD, then L, so I am adding 2
        index = grid + 1

        # replace the zero in the array with the correct percent for grids which have a value here
        zeros_array[index] = percent

    # creates coloumn names for the dataframe: hour, then grid numbers
    column_list = ['hour', 'calculated_sum']
    for i in range(1, 43):
        column_list.append(str(i))

    # creates dataframe object
    dfObj = pd.DataFrame([zeros_array], columns=column_list)

    # combines the old and new dataframe
    new_df = pd.concat([existing_df, dfObj])

    new_df.to_csv(csv_path,
                  index=False)


def determine_which_model_files(model_site_dict, DOYstart_mod, DOYstop_mod, run, instrument, sample, variable,
                                obs_level, model_format, disheight, z0zdlist, saveyn, savepath):
    # finds all the grids which will be needed - looks through the whole model site dict and gets all grid numbers
    # across whole time range chosen

    # list which will include all grid numbers
    # made as a set to avoid repeats
    all_items_set = set([])

    for hour in model_site_dict:
        for grid_num in model_site_dict[hour]:
            all_items_set.add(grid_num)

    model_site_for_sort = []
    for grid in sorted(list(all_items_set)):
        model_site_for_sort.append(int(grid))

    model_site_sorted = sorted(model_site_for_sort)

    model_site = []
    for item in model_site_sorted:
        model_site.append(str(item))

    # dictionary to append model data to, for all sites chosen.
    included_grids = {}

    # for every grid chosen & present in list:
    for grid in model_site:
        print(' ')
        print(' ')
        print(
            '---------------------------------------------------------------------------------------------------')
        print(' ')
        print('GRID NUMBER CHOSEN: ', grid)

        # changes to int
        grid = int(grid)

        # For this grid:

        # calling grid_dict from variables.py to see what sites include this grid as part of their 3x3
        # varaibles.py
        print('Options with this grid number are: ', look_up.grid_dict[grid])

        # Step 1:
        # makes lists for sites and grid litters for all items called from variables.py,
        # in order to find files for them (based on what is present in the grid_dict)

        # list of sites
        sites_present = []
        # list of corresponding grid letters
        grid_letters = []

        # for each site which includes the chosen grid
        for item in look_up.grid_dict[grid]:
            # split the items present in the dict to get a site name and a grid letter
            site_present = item.split(' ')[0]
            grid_letter = item.split(' ')[1]

            # append them to the lists above
            sites_present.append(site_present)
            grid_letters.append(grid_letter)

        # Step 2:
        # finds files for all sites containing the current grid choice

        # list to append found file dicts to
        dict_list = []
        # list to append the keys of the found file dicts to
        # keys are strings of like, model type and date
        key_list = []

        # for every site which includes our grid in it's 3x3
        for sitei in sites_present:
            # finds the files for the site
            print(' ')

            print(' ')
            print('FINDING FILES FOR SITE: ', sitei)
            file_dict_ukv = file_read.finding_files(model_format,
                                                    'ukv',
                                                    DOYstart_mod,
                                                    DOYstop_mod,
                                                    sitei,
                                                    run,
                                                    instrument,
                                                    sample,
                                                    variable,
                                                    obs_level,
                                                    model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                    )

            # append the keys to key_list
            list_of_keys = file_dict_ukv.keys()
            key_list.append(list_of_keys)

        # append the dictionaries to dict_list
        dict_list.append(file_dict_ukv)

        # Step 3: Put together a collection of unique files found for each day chosen, for this grid.
        # This maximises the data availability for the model -
        # As one site (example, IMU) may have it's grid A matching with our chosen grid, and another site (BCT)
        # may have it's grid E also matching, but files are available for IMU which aren't for BCT...

        # Takes the key_list, which is a list of lists (list of lists of keys for all sites' files found)
        # and then finds all the unique items (gets rid of keys which appear more than once throughout all the
        # sites
        unique_keys = list(set(x for l in key_list for x in l))

        # Creates a dictionary to keep a collection of as-complete-as-possible files found for this grid
        complete_files = {}

        # for each unique key
        for item in unique_keys:

            # for dicts in list of dicts (one for each site)
            for dict in dict_list:

                # if the unique key is in this dict
                if item in dict:

                    # define unique item in new dict
                    complete_files[item] = dict[item]

                    # and then this item has been found, so no longer need to look for this unique key
                    # break the loop here
                    break

                # if the item was not in this dict, keep looking
                else:
                    pass

        # Step 4: Find the corresponding sites and grid letters which this new collection of unique file items
        # correspond to

        # Finding the site string for each site used in the unique collection
        # defines a list of sites used
        sites_used = []

        # for every item in the unique file collection
        for item in sorted(complete_files):
            # get the site which corresponds to this key
            # split by underscore, get the last item: example KSSW.nc, use [:-3] to get rid of .nc
            site_here = complete_files[item][0].split('_')[-1][:-3]

            # append to list of sites used
            sites_used.append(site_here)

        # Finding the grid letter for each site used in the unique collection
        # defines a list of letters used
        grid_letters_used = []

        # for every site used
        for item in sites_used:
            # find where this appears in sites present, and from that, can get the letter
            letter = np.asarray(grid_letters)[np.where(np.asarray(sites_present) == item)][0]

            # append to list
            grid_letters_used.append(letter)

        # Step 5: Finding where site changes occur
        # eventually will contribute to splitting up the complete dictionary up into chunks of the same site.
        # This is because the sort_models function can only take one site/ grid letter at once.

        # define list of indexes where site changes within the sites_used list
        # (sites_used being a list of sites included within the complete collection)
        site_change = []
        # for the index between 0 and the length of the complete collection
        for i in range(0, len(sites_used)):

            # if it is not the first index
            if i != 0:

                # if the current site is not the same as the previous site, there is a site change and the index (i)
                # is appended
                if sites_used[i] != sites_used[i - 1]:
                    site_change.append(i)

        # if there are no changes, the site change list == []
        # so need to append a 0 to get first and only site used
        if len(site_change) == 0:
            site_change.append(0)

        # Step 6: Splits up the complete dictionary KEYS up into chunks of the same site.

        # creating a list of lists
        # This will be be lists of keys from the complete collection - separated by differing sites used
        list_of_lists = []

        # if the length of the site changes is more than one
        # meaning more than one site is included here
        if len(site_change) != 1:

            # Defining the first list (for the first site)
            # append all keys until the first index change
            list_of_lists.append(sorted(complete_files.keys())[:site_change[0]])

            # Defining all the middle lists
            # makes list of tuples of 2 indices to slice by
            indices_tuple = []
            # for all indices in between the first and last
            for i in range(1, len(site_change)):
                # defines pair of indicies to slice by (in form of tuple)
                tuple = site_change[i - 1], site_change[i]
                # appends
                indices_tuple.append(tuple)
            # slice list by these tuples
            for item in [sorted(complete_files.keys())[s:e] for s, e in indices_tuple]:
                # append to list of lists
                list_of_lists.append(item)

            # Defining the last list
            # append all the keys from the last index change to the end of the complete keys
            list_of_lists.append(sorted(complete_files.keys())[site_change[-1]:])

        # If only one site is included
        else:
            list_of_lists.append(sorted(complete_files.keys())[site_change[-1]:])

        # Step 7: Splits up the complete dictionary (no longer just keys, but values too)
        # up into chunks of the same site.

        # creates list to append dictionaries to (one for each site used in chunks)
        list_of_dicts = []

        # for every list in list of lists, or, for every chunk of consecutive sites used in complete collection:
        for listi in list_of_lists:
            # define a dictionary
            temp_dict = {}
            # for every item (which is a key in the complete collection) in this current list
            for item in listi:
                # defines an item in the new dictionary, by calling the item from the original dictionary
                temp_dict[item] = complete_files[item]
            # append this temporary dictionary to my list of dictionaries.
            list_of_dicts.append(temp_dict)

        # Step 8: Gets a list of sites and grid letters - one for each dictionary of files for
        # each site (one for each cluster)

        # Creates lists of sites and grid letters which the list of dicts correspond to
        # so one site and grid letter per dictionary of files

        # defines lists of sites and grid letters
        list_of_sites_for_final = []
        list_of_grids_for_final = []

        # append the first item
        list_of_sites_for_final.append(sites_used[0])
        list_of_grids_for_final.append(grid_letters_used[0])

        # appends the further items, using list of indicies where changes occured
        for item in site_change:
            list_of_sites_for_final.append(sites_used[item])
            list_of_grids_for_final.append(grid_letters_used[item])

        # Step 9: Defines empty lists for the output of sort_models to be appended to.

        # dict of datetimes
        # lontimedict
        combined_ukv0_list = []
        # dict of temps
        # lontempdict
        combined_ukv1_list = []
        # dict of temp 9
        # lontempdict9
        combined_ukv2_list = []
        # dict of temp 0
        # lontempdict0
        combined_ukv3_list = []
        # dict of temp 2
        # lontempdict2
        combined_ukv4_list = []
        # list of strings time
        # stringtimelon
        combined_ukv5_list = []
        # list of strings temp
        # stringtemplon
        combined_ukv6_list = []
        # list of strings temp9
        # stringtemplon9
        combined_ukv7_list = []
        # list of strings temp 0
        # stringtemplon0
        combined_ukv8_list = []
        # list of strings temp2
        # stringtemplon2
        combined_ukv9_list = []

        # ToDo: I REALLY NEED TO CHANGE THIS!
        # Heights atm are changing with grid because of the sites are different - so I need to change this
        # This will be the case when a stash code is used which ISN'T from the surface

        # height of model
        # modheightvaluelon
        combined_ukv10_list = []
        # height of model0
        # modheightvaluelon0
        combined_ukv11_list = []
        # height of model2
        # modheightvaluelon2
        combined_ukv12_list = []
        # alllontimes
        combined_ukv13_list = []

        # Step 10: Runs sort models for each cluster of files, and appends output.

        for file_dict_ukv, site_item, grid_item in zip(list_of_dicts, list_of_sites_for_final,
                                                       list_of_grids_for_final):
            # pulls the start and stop DOY for this cluster from the dictionary key
            DOYstart_temp = int(list(file_dict_ukv.keys())[0][3:])
            DOYstop_temp = int(list(file_dict_ukv.keys())[-1][3:])

            # ordering UKV model files
            # file_read.py
            files_ukv = file_read.order_model_stashes('ukv', file_dict_ukv, variable)

            # sort models
            # models.py
            ukv = sort_model.sort_models(variable, 'ukv', files_ukv, disheight, z0zdlist, DOYstart_temp, DOYstop_temp,
                                         site_item, saveyn,
                                         savepath, model_format, grid_item)

            # appends outputs to lists
            combined_ukv0_list.append(ukv[0])
            combined_ukv1_list.append(ukv[1])
            combined_ukv2_list.append(ukv[2])
            combined_ukv3_list.append(ukv[3])
            combined_ukv4_list.append(ukv[4])
            combined_ukv5_list.append(ukv[5])
            combined_ukv6_list.append(ukv[6])
            combined_ukv7_list.append(ukv[7])
            combined_ukv8_list.append(ukv[8])
            combined_ukv9_list.append(ukv[9])
            combined_ukv10_list.append(ukv[10])
            combined_ukv11_list.append(ukv[11])
            combined_ukv12_list.append(ukv[12])
            combined_ukv13_list.append(ukv[13])

        # Step 11: Combines outputs into one item for each output

        # combines dictionaries
        combined_ukv0 = {}
        for d in combined_ukv0_list:
            combined_ukv0.update(d)
        combined_ukv1 = {}
        for d in combined_ukv1_list:
            combined_ukv1.update(d)
        combined_ukv2 = {}
        for d in combined_ukv2_list:
            combined_ukv2.update(d)
        combined_ukv3 = {}
        for d in combined_ukv3_list:
            combined_ukv3.update(d)
        combined_ukv4 = {}
        for d in combined_ukv4_list:
            combined_ukv4.update(d)

        # combines lists
        combined_ukv5 = sum(combined_ukv5_list, [])
        combined_ukv6 = sum(combined_ukv6_list, [])
        combined_ukv7 = sum(combined_ukv7_list, [])
        combined_ukv8 = sum(combined_ukv8_list, [])
        combined_ukv9 = sum(combined_ukv9_list, [])
        combined_ukv13 = sum(combined_ukv13_list, [])

        # takes the height (currently botched)
        # ToDo: edit this - as multiple sites will have more than one height
        temp_height_botch = combined_ukv10_list[0]

        # Step 12: Appends the outputs into the included_grids dictionary (one grouped output per grid)
        # This then acts as 'included_models'

        # groups the outputs for the time series plots
        # [ stringtimelon,  stringtemplon,  lontimedict,    lontempdict,    modheightvaluelon   ]
        group_ukv = [combined_ukv5, combined_ukv6, combined_ukv0, combined_ukv1, temp_height_botch]

        # appends to dictionary
        included_grids[grid] = group_ukv

    return included_grids, model_site


def average_model_grids(included_grids, DOYstart_mod, DOYstop_mod, percentage_vals_dict, model_site_dict, model_site):
    # Defining a big list for averaging values
    list_to_average = []
    list_of_times = []
    list_of_temp_strings = []
    list_of_time_strings = []
    list_of_heights = []

    for grid in sorted(included_grids):
        # appends to appropriate lists
        stringtimelon = included_grids[grid][0]
        stringtemplon = included_grids[grid][1]
        lontimedict = included_grids[grid][2]
        lontempdict = included_grids[grid][3]
        modheightvaluelon = included_grids[grid][4]

        list_of_times.append(lontimedict)
        list_to_average.append(lontempdict)
        list_of_temp_strings.append(stringtemplon)
        list_of_time_strings.append(stringtimelon)
        list_of_heights.append(modheightvaluelon)

    # tests to see if all the times are the same between all the grids chosen
    # defines function to do this
    def all_same(items):
        return all(x == items[0] for x in items)

    # tests the times
    if all_same(list_of_times):
        # if all the same, continue on
        pass
    else:
        # if times are different
        print(' ')
        print('THERES A PROBLEM! TIMES ARE DIFFERENT!')
        sys.exit()

    # because all the sting lists are the same, I can take the first one:

    # error with missing observations - cannot take the index of empty list
    strings = list_of_temp_strings[0]

    # gets datetime objects of the day(s) I want
    DOYstart_dt = datetime.strptime(str(DOYstart_mod), '%Y%j')
    DOYstop_dt = datetime.strptime(str(DOYstop_mod + 2),
                                   '%Y%j')  # + 1 because it's a forecast so I need file from day before.
    # And another + 1 because these times are at midnight
    # (so I need midnight of next dat

    new_list_of_times = []
    new_list_to_average = []

    # list_of_times = list of dictionaries, keys as day. Each dictionary is a grid
    for grid_time, grid_val in zip(list_of_times, list_to_average):

        grid_dict_times = {}
        grid_dict_vals = {}

        for day_time, day_val in zip(list_of_time_strings[0],
                                     list_of_temp_strings[0]):  # is the same as the rest (as passed the test above)

            temp_day_time = []
            temp_day_vals = []

            for time, val in zip(grid_time[day_time], grid_val[day_val]):

                if DOYstart_dt <= time < DOYstop_dt:
                    temp_day_time.append(time)
                    temp_day_vals.append(val)

            # prevents empty dicts (as I'm getting rid of midnight from the end DOY - this causes empty lists
            if len(temp_day_time) != 0:
                grid_dict_times[day_time] = temp_day_time
                grid_dict_vals[day_val] = temp_day_vals

        new_list_of_times.append(grid_dict_times)
        new_list_to_average.append(grid_dict_vals)

    # dict to average by hour - key is date string for each hour included, values are QH vals for each grid
    hour_dict = {}

    for grid in new_list_of_times:

        # for each day (or day string)
        # gets rid of the last day string (as it used to just contain midnight which now isn't a thing)
        for day in list_of_time_strings[0]:

            for hour in grid[day]:
                time_string = hour.strftime("%y%m%d%H")
                hour_dict[time_string] = []

    for grid_time, grid_val in zip(new_list_of_times, new_list_to_average):

        # for each day (or day string)
        for day_time, day_val in zip(list_of_time_strings[0], strings):

            for hour_time, hour_val in zip(grid_time[day_time], grid_val[day_val]):
                time_string = hour_time.strftime("%y%m%d%H")

                hour_dict[time_string].append(hour_val)

    if sorted(percentage_vals_dict) == sorted(model_site_dict) == sorted(hour_dict):
        pass
    else:
        print(' ')
        print("KEYS DON'T MATCH")
        print(' ')
        print(sorted(percentage_vals_dict))
        print(' ')
        print(sorted(model_site_dict))
        print(' ')
        print(sorted(hour_dict))

        if model_site_dict == percentage_vals_dict:
            pass
        else:
            mutual_keys_1 = list(set(model_site_dict).intersection(percentage_vals_dict))

            to_delete_1a = set(model_site_dict.keys()).difference(mutual_keys_1)
            to_delete_1b = set(percentage_vals_dict.keys()).difference(mutual_keys_1)

            print(' ')
            print('to_delete_1a: ', to_delete_1a)
            print('to_delete_1b: ', to_delete_1b)

            for d in to_delete_1a:
                del model_site_dict[d]

            for d in to_delete_1b:
                del percentage_vals_dict[d]

        if hour_dict == percentage_vals_dict:
            pass
        else:
            # hour_dict = list(set(hour_dict).intersection(percentage_vals_dict))

            mutual_keys_2 = list(set(hour_dict).intersection(percentage_vals_dict))

            to_delete_2a = set(hour_dict.keys()).difference(mutual_keys_2)
            to_delete_2b = set(percentage_vals_dict.keys()).difference(mutual_keys_2)

            print(' ')
            print('to_delete_2a: ', to_delete_2a)
            print('to_delete_2b: ', to_delete_2b)

            for d in to_delete_2a:
                del hour_dict[d]

            for d in to_delete_2b:
                del percentage_vals_dict[d]

        if hour_dict == model_site_dict:
            pass
        else:
            # hour_dict = list(set(hour_dict).intersection(model_site_dict))

            mutual_keys_3 = list(set(hour_dict).intersection(model_site_dict))

            to_delete_3a = set(hour_dict.keys()).difference(mutual_keys_3)
            to_delete_3b = set(model_site_dict.keys()).difference(mutual_keys_3)

            print(' ')
            print('to_delete_3a: ', to_delete_3a)
            print('to_delete_3b: ', to_delete_3b)

            for d in to_delete_3a:
                del hour_dict[d]

            for d in to_delete_3b:
                del model_site_dict[d]

        # sys.exit()

    # all grid - to get order
    inclu_av_grids = {}

    for hour in sorted(hour_dict):

        inclu_av_grids[hour] = []

        for grid_num in model_site_dict[hour]:
            index_of_grid = np.where(np.asarray(model_site) == grid_num)[0][0]
            inclu_av_grids[hour].append(hour_dict[hour][index_of_grid])

    w_av_per_hour = {}
    av_per_hour = {}
    for hour in sorted(hour_dict):
        print(hour)
        print(hour_dict[hour])
        print(model_site)
        print(model_site_dict[hour])
        print(percentage_vals_dict[hour])
        print(inclu_av_grids[hour])
        print(np.average(inclu_av_grids[hour], axis=0, weights=percentage_vals_dict[hour]))
        print(np.average(inclu_av_grids[hour], axis=0))
        print(' ')

        w_av_per_hour[hour] = np.average(inclu_av_grids[hour], axis=0, weights=percentage_vals_dict[hour])
        av_per_hour[hour] = np.average(inclu_av_grids[hour], axis=0)

    # getting it back into the correct format
    w_averaged_dict = {}
    w_averaged_dict_time = {}

    # # dictionary of averaged values for each day
    average_dict = {}
    average_dict_time = {}

    for hour in sorted(w_av_per_hour):
        dt_ob = datetime.strptime(hour, '%y%m%d%H')
        # I want a string for the day before the content is forcatsed for (as it's a forecast the day before)
        doy_string = dt_ob.strftime("%Y%j")

        doy_num = int(doy_string) - 1  # - 1 because I want the day before - as it's a forcast
        date_string = str(doy_num)

        string_construct = 'tempukv' + date_string
        string_construct_time = 'timeukv' + date_string

        w_averaged_dict[string_construct] = []
        w_averaged_dict_time[string_construct_time] = []

        average_dict[string_construct] = []
        average_dict_time[string_construct_time] = []

    for hour in sorted(w_av_per_hour):
        dt_ob = datetime.strptime(hour, '%y%m%d%H')
        doy_string = dt_ob.strftime("%Y%j")

        doy_num = int(doy_string) - 1  # - 1 because I want the day before - as it's a forcast
        date_string = str(doy_num)

        string_construct = 'tempukv' + date_string
        string_construct_time = 'timeukv' + date_string

        w_averaged_dict[string_construct].append(w_av_per_hour[hour])
        average_dict[string_construct].append(av_per_hour[hour])

        w_averaged_dict_time[string_construct_time].append(dt_ob)
        average_dict_time[string_construct_time].append(dt_ob)

    # grouping thr average values
    # [ stringtimelon,  stringtemplon,  lontimedict,    lontempdict,    modheightvaluelon   ]
    # average_grouped = [list_of_time_strings[0], strings, new_list_of_times[0], average_dict, list_of_heights[0]]
    average_grouped = [sorted(average_dict_time.keys()), sorted(average_dict.keys()), average_dict_time, average_dict,
                       list_of_heights[0]]

    included_grids['Average'] = average_grouped

    # weighted average groups
    # [ stringtimelon,  stringtemplon,  lontimedict,    lontempdict,    modheightvaluelon   ]
    # w_average_grouped = [list_of_time_strings[0], strings, new_list_of_times[0], w_averaged_dict,
    #                      list_of_heights[0]]

    w_average_grouped = [sorted(w_averaged_dict_time.keys()), sorted(w_averaged_dict.keys()), w_averaged_dict_time,
                         w_averaged_dict,
                         list_of_heights[0]]

    included_grids['WAverage'] = w_average_grouped

    return included_grids
