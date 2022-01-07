import netCDF4 as nc




def extract_ukv_z0(file_dict, grid_choice=0):
    """
    Get model roughness length from file with stash code m01s03i026
    :return:
    """

    for day in sorted(file_dict.keys()):


        filepath = file_dict[day][0]

        nc_file = nc.Dataset(filepath)

        z0_var_obj = nc_file.variables['surface_roughness_length']


        if grid_choice == 0:
            # Defult val goes to centre grid, otherwise known as grid 'E':
            index_lat = 1
            index_lon = 1
        elif grid_choice == 'A':
            index_lat = 2
            index_lon = 0
        elif grid_choice == 'B':
            index_lat = 2
            index_lon = 1
        elif grid_choice == 'C':
            index_lat = 2
            index_lon = 2
        elif grid_choice == 'D':
            index_lat = 1
            index_lon = 0
        elif grid_choice == 'E':
            index_lat = 1
            index_lon = 1
        elif grid_choice == 'F':
            index_lat = 1
            index_lon = 2
        elif grid_choice == 'G':
            index_lat = 0
            index_lon = 0
        elif grid_choice == 'H':
            index_lat = 0
            index_lon = 1
        elif grid_choice == 'I':
            index_lat = 0
            index_lon = 2



        print(z0_var_obj[index_lat, index_lon, :])

        print(day)


    print('end')



from scint_eval.functions import file_read
DOYstart_mod = 2016142
DOYstop_mod = 2016142
run = '21Z'
# roughness length
file_dict_ukv_z0 = file_read.finding_files('new',
                                             'ukv',
                                             DOYstart_mod,
                                             DOYstop_mod,
                                             'RGS',
                                             run,
                                             'Davis',
                                             '15min',
                                             'z0',
                                             'L2',
                                             model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                             )
extract_ukv_z0(file_dict_ukv_z0, 'I')





