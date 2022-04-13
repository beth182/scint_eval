import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np

from scint_eval import look_up

from scint_eval.functions import file_read
from scint_eval.functions import sort_model
from scint_eval.functions import array_retrieval


def get_ukv_KSSW_kdown(DOY_model):
    """

    :return:
    """


    file_dict_ukv_kdown_KSSW = file_read.finding_files('new',
                                                       'ukv',
                                                       DOY_model,
                                                       DOY_model,
                                                       'KSSW',
                                                       '21Z',
                                                       'LASMkII_Fast',
                                                       '1min',
                                                       'kdown',
                                                       'L1',
                                                       # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                       model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                       )
    files_ukv_kdown_KSSW = file_read.order_model_stashes('ukv', file_dict_ukv_kdown_KSSW, 'kdown')
    ukv_kdown_KSSW = sort_model.sort_models('kdown', 'ukv', files_ukv_kdown_KSSW, 0, DOY_model, DOY_model,
                                            'KSSW', 'C:/Users/beths/Desktop/LANDING/', 'new', grid_choice='E')
    included_models_kdown_KSSW = {}
    group_ukv_kdown_KSSW = [ukv_kdown_KSSW[5], ukv_kdown_KSSW[6], ukv_kdown_KSSW[0], ukv_kdown_KSSW[1],
                            ukv_kdown_KSSW[10]]
    included_models_kdown_KSSW['ukv'] = group_ukv_kdown_KSSW
    mod_time_kdown_KSSW, mod_vals_kdown_KSSW = array_retrieval.retrive_arrays_model(included_models_kdown_KSSW, 'ukv')

    return mod_time_kdown_KSSW, mod_vals_kdown_KSSW



def weight_lc_fractions(model_site_dict, percentage_vals_dict, DOYstart,
                        lc_csv='C:/Users/beths/OneDrive - University of Reading/landuse/site grids/10-tile landuse (Maggie_new)/landuse_csv_files/all_grids_10T.csv'):
    """

    :return:
    """

    assert model_site_dict.keys() == percentage_vals_dict.keys()


    # read in csv df
    lc_df = pd.read_csv(lc_csv)

    weighted_lc_dfs = []


    for hour in model_site_dict.keys():

        grid_numbers = model_site_dict[hour]
        grid_weights = percentage_vals_dict[hour]

        grid_lc_df_list_unweighted = []
        grid_lc_df_list_weighted = []

        for grid, weight in zip(grid_numbers, grid_weights):

            grid = int(grid)
            # find the grid in the lc df
            target_lc_df = lc_df.loc[lc_df['GRID_NUM'] == grid]
            target_lc_df = target_lc_df.set_index('GRID_NUM')

            grid_lc_df_list_unweighted.append(target_lc_df)

            # apply weighting
            weight = weight / 100

            weighted_df = target_lc_df * weight

            grid_lc_df_list_weighted.append(weighted_df)

        combine_weighted_df = pd.concat(grid_lc_df_list_weighted)

        combine_weighted_df.loc['W_SUM'] = combine_weighted_df.sum(numeric_only=True, axis=0)
        assert np.isclose(combine_weighted_df.loc['W_SUM'].sum(), 1)

        for i in combine_weighted_df.index:
            if type(i) != str:
                combine_weighted_df.drop(i, inplace=True)

        combine_weighted_df.index = [hour]
        weighted_lc_dfs.append(combine_weighted_df)

    df = pd.concat(weighted_lc_dfs)

    df.to_csv('C:/Users/beths/Desktop/LANDING/weighted_lc_ukv_' + str(DOYstart) + '.csv')

    return df


def pytest_landcover_csvs(
        landuse_dir='C:/Users/beths/OneDrive - University of Reading/landuse/site grids/10-tile landuse (Maggie_new)/landuse_csv_files/'):
    # python tests to make sure landcover files are as we expect
    for key in look_up.grid_dict_lc.keys():

        print('GRID NUMBER: ', key)

        # define the list of grid strings (site_letter) for this grid number
        key_list = look_up.grid_dict_lc[key]

        # list to append dataframes to cor checking
        # will be including the grid col and original index
        key_vals_check = []

        for grid_code in key_list:
            print('Grid code:', grid_code)

            # split the string to get site code and grid letter
            site = grid_code.split(' ')[0]
            letter = grid_code.split(' ')[1]

            # find the csv based on above
            file_path = landuse_dir + site + '_10T.csv'

            # read the whole csv file
            df = pd.read_csv(file_path)

            # lock on to just the row of the grid letter I want
            lc_df = df.loc[df['GRID'] == letter]

            # append this 1 row df to list
            key_vals_check.append(lc_df)

        # reset the index and drop the GRID column to enable comparison
        df_to_check = []
        for df in key_vals_check:
            df = df.drop('GRID', 1)
            df = df.reset_index(drop=True)
            df_to_check.append(df)

        # make the checks to see if all df in the list equal to the first
        for df in df_to_check:
            assert_frame_equal(df, df_to_check[0])

        print('All passed')
        print(' ')


def create_grid_lc_csv(
        landuse_dir='C:/Users/beths/OneDrive - University of Reading/landuse/site grids/10-tile landuse (Maggie_new)/landuse_csv_files/'):
    # Compile an overall csv file for grids 1 - 42
    list_of_grid_df = []
    for key in look_up.grid_dict_lc.keys():
        # take the first grid for this number
        grid_code = look_up.grid_dict_lc[key][0]

        # split the string to get site code and grid letter
        site = grid_code.split(' ')[0]
        letter = grid_code.split(' ')[1]

        # find the csv based on above
        file_path = landuse_dir + site + '_10T.csv'

        # read the whole csv file
        df = pd.read_csv(file_path)

        # lock on to just the row of the grid letter I want
        lc_df = df.loc[df['GRID'] == letter]

        lc_df = lc_df.drop('GRID', 1)
        lc_df.index = [key]
        lc_df.index.names = ['GRID_NUM']

        list_of_grid_df.append(lc_df)

    df = pd.concat(list_of_grid_df)
    df.to_csv(landuse_dir + 'all_grids_10T.csv')
    print('end')


def check_KSSW_issue_stashcodes():
    # get model data from MR and KSSW  - and see if they match up - FOR STASH CODES
    from scint_eval.functions import file_read
    from scint_eval.functions import sort_model
    from scint_eval.functions import array_retrieval
    file_dict_ukv_kdown_KSSW = file_read.finding_files('new',
                                                       'ukv',
                                                       2016122,
                                                       2016122,
                                                       'KSSW',
                                                       '21Z',
                                                       'LASMkII_Fast',
                                                       '1min',
                                                       'kdown',
                                                       'L1',
                                                       # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                       model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                       )
    files_ukv_kdown_KSSW = file_read.order_model_stashes('ukv', file_dict_ukv_kdown_KSSW, 'kdown')
    ukv_kdown_KSSW = sort_model.sort_models('kdown', 'ukv', files_ukv_kdown_KSSW, 0, 2016123, 2016123,
                                            'KSSW', 'C:/Users/beths/Desktop/LANDING/', 'new', grid_choice='A')
    included_models_kdown_KSSW = {}
    group_ukv_kdown_KSSW = [ukv_kdown_KSSW[5], ukv_kdown_KSSW[6], ukv_kdown_KSSW[0], ukv_kdown_KSSW[1],
                            ukv_kdown_KSSW[10]]
    included_models_kdown_KSSW['ukv'] = group_ukv_kdown_KSSW
    mod_time_kdown_KSSW, mod_vals_kdown_KSSW = array_retrieval.retrive_arrays_model(included_models_kdown_KSSW, 'ukv')

    print('END')

    file_dict_ukv_kdown_MR = file_read.finding_files('new',
                                                     'ukv',
                                                     2016122,
                                                     2016122,
                                                     'MR',
                                                     '21Z',
                                                     'LASMkII_Fast',
                                                     '1min',
                                                     'kdown',
                                                     'L1',
                                                     # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                     model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                     )
    files_ukv_kdown_MR = file_read.order_model_stashes('ukv', file_dict_ukv_kdown_MR, 'kdown')
    ukv_kdown_MR = sort_model.sort_models('kdown', 'ukv', files_ukv_kdown_MR, 0, 2016123, 2016123,
                                          'MR', 'C:/Users/beths/Desktop/LANDING/', 'new', grid_choice='E')
    included_models_kdown_MR = {}
    group_ukv_kdown_MR = [ukv_kdown_MR[5], ukv_kdown_MR[6], ukv_kdown_MR[0], ukv_kdown_MR[1], ukv_kdown_MR[10]]
    included_models_kdown_MR['ukv'] = group_ukv_kdown_MR
    mod_time_kdown_MR, mod_vals_kdown_MR = array_retrieval.retrive_arrays_model(included_models_kdown_MR, 'ukv')
