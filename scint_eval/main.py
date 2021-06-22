from calendar import isleap
import os

from scint_eval.functions import file_read


def main(obs_site, DOYstart, DOYstop, variable, savepath, saveyn, run, instrument, sample,
         format, obs_level, scint_path):
    """
    MAIN FUNCTION FOR NEW FILE FORMAT MODEL FILES.
    """

    ################################################################################################################
    # if the files are from the 21Z run, then we need to pick files from the DOY before the chosen range
    # this is because we discount the first 3 hours of the files, so we start at midnight the day after the startDOY...
    if run == '21Z':
        # string out of the chosen starting DOY and year
        str_year = str(DOYstart)[:4]
        str_DOY = str(DOYstart)[4:]
        # if the start DOY is the first day of the year:
        if str_DOY == '001':
            # we now have to start with the year before the chosen year
            new_start_year = int(str_year) - 1
            # to get the start DOY, we need to know what the last DOY of the previous year is
            # so is it a leap year (366 days) or not?
            if isleap(new_start_year):
                # leap year
                new_start_DOY = 366
            else:
                # normal year
                new_start_DOY = 365
            # combining the new start year and new DOY start
            DOYstart_mod = int(str(new_start_year) + str(new_start_DOY))
        else:
            new_start_DOY = str(int(str_DOY) - 1).zfill(3)
            DOYstart_mod = int(str_year + new_start_DOY)
    else:
        DOYstart_mod = DOYstart
    DOYstop_mod = DOYstop - 1

    ################################################################################################################
    # finding observation files
    # file_read.py
    files_obs = file_read.finding_files(format, 'obs', DOYstart, DOYstop, obs_site, run, instrument, sample,
                                        variable, obs_level,
                                        "Z:/micromet/Tier_processing/rv006011/new_data_storage/",
                                        "Z:/micromet/Tier_processing/rv006011/new_data_scint/data/"
                                        )


    print('END')


########################################################################################################################
# c h o i c e s
DOYstart_choice = 2016142
DOYstop_choice = 2016142

sample = '15min'
obs_level = 'L1'
run = '21Z'

# For scintillometry, variable is always sensible heat currently - needn't ever change this
variable = 'H'

# Description of paths can be seen at
# https://docs.google.com/spreadsheets/d/1gajURSbBKqc0sUAjd-cStRCjUIeh30U2i6GGeRuV-yE/edit#gid=996311903
# all path numbers can re referenced back to here
scint_paths = [12, 14, 15]
scint_path = scint_paths[0]
########################################################################################################################


# currently the paths options are
if scint_path == 12:
    # PATH #12 -- LAS mk11 -- BCT -> IMU -- 0992014 - 3042018
    instrument = 'LASMkII_Fast'
    # defines which site to take the obs from
    # This will always be the site where the receiver is located
    obs_site = 'IMU'

elif scint_path == 15:
    # PATH #15 -- LAS mk11 -- SCT -> SWT -- 2372017 - CURRENT
    instrument = 'LASMkII_Fast'
    obs_site = 'SWT'

elif scint_path == 14:
    # PATH #14 -- BLS -- IMU -> SWT -- 0962017 - CURRENT
    instrument = 'BLS'
    obs_site = 'SWT'

else:
    instrument = None
    obs_site = None
    raise ValueError('Path chosen not an option.')

file_format = ['old', 'new']
format = file_format[1]

if __name__ == "__main__":

    # Join list items using join()
    site_string = obs_site

    folder_name = str(DOYstart_choice) + '_' + str(DOYstop_choice) + '_' + variable + '_' + site_string + '_' + str(
        scint_path) + '/'
    save_folder = '../plots/' + folder_name

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    main(obs_site, DOYstart_choice, DOYstop_choice, variable, save_folder, 1, run,
         instrument, sample, format, obs_level, scint_path)

print(' ')
print(' ')
print('FINISH')

