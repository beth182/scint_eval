def roughness_and_displacement(z01,
                               z0m,
                               z0o,
                               zdo):
    """
    Stores roughness and displacement heights in a list.

    :param z01: z0 for the 1-tile - 1
    :param z0m: z0 for MORUSES - 0.8
    :param z0o: z0 for observations - Taken from variables.py
    :param zdo: zd for observations - Taken from variables.py

    :return z0zd_list: List of different roughness lengths and displacement heights for the models and observations.
    z01, z0m, z0o, zdo, z0do (where z0do is the combination of z0o and zdo).
    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Defining Roughness Length and Displacement Height')
    print(' ')

    z0do = zdo + z0o  # combination of z0 and zd for observations
    z0zd_list = [z01, z0m, z0o, zdo, z0do]

    return z0zd_list
