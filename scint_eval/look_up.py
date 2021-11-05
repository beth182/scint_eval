import sys

# models that are avalible and their settings
# 0 - file name preface
# 1 - model colour for plotting
# 2 - z0_index
model_options = {'ukv': ['MOUKV_FC', 'b', 0],
                 'lon': ['MOLON_FC', 'r', 1],
                 'mor': ['MOMOR_FC', 'purple', 1]}


def find_altitude(site,
                  model):
    """
    Function to feed model altitude into sort models
    :param site: site in the format taken from the site_format dict in variables
    :param model: which model I am looking to get altitude for
    :return: altitude
    """

    if model == 'ukv':
        altitude = UKV_site_altitudes[site]
    elif model == 'lon' or model == 'mor':
        altitude = LON_site_altitudes[site]
    else:
        print('model choice not an option.')
        sys.exit()

    return altitude


# for MODEL files -- OLD FORMAT
sites_old_format = {'BCT': 'DAVIS_BCT',
                    'IMU': 'DAVIS_IMU',
                    'IML': 'DAVIS_IML',
                    'BFCL': 'DAVIS_BFCL',
                    'KSSW': 'WXT_KSSW'}

# for MODEL files -- new format
sites = {'Heathrow': 'Heathrow',
         'BCT': 'LON_BCT',
         'BFCL': 'LON_BFCL',
         'BGH': 'LON_BGH',
         'BTT': 'LON_BTT',
         'IML': 'LON_IML',
         'IMU': 'LON_IMU',
         'KSSW': 'LON_KSSW',
         'MR': 'LON_MR',
         'NK': 'LON_NK',
         'RGS': 'LON_RGS',
         'SWT': 'LON_SWT',
         'Reading': 'Reading'}
site_names = sites.keys()

# for MODEL files, new format - stash codes of all variables
stash = {'m01s00i002': 'U COMPNT OF WIND AFTER TIMESTEP',
         'm01s00i003': 'V COMPNT OF WIND AFTER TIMESTEP',
         'm01s00i010': 'SPECIFIC HUMIDITY AFTER TIMESTEP',
         'm01s00i024': 'SURFACE TEMPERATURE AFTER TIMESTEP',
         'm01s00i025': 'BOUNDARY LAYER DEPTH AFTER TIMESTEP',
         'm01s00i090': 'TOTAL AEROSOL (FOR VISIBILITY)',
         'm01s00i150': 'W COMPNT OF WIND AFTER TIMESTEP',
         'm01s00i266': 'BULK CLOUD FRACTION IN EACH LAYER',
         'm01s00i272': 'RAIN AFTER TIMESTEP',
         'm01s00i408': 'PRESSURE AT THETA LEVELS AFTER TS',
         'm01s00i409': 'SURFACE PRESSURE AFTER TIMESTEP',
         'm01s03i026': 'ROUGHNESS LENGTH AFTER TIMESTEP',
         'm01s03i202': 'HT FLUX FROM SURF TO DEEP SOIL LEV 1',
         'm01s03i216': 'BOUNDARY LAYER HEAT FLUXES W/M2',
         'm01s03i217': 'SURFACE SENSIBLE HEAT FLUX W/M2',
         'm01s03i219': 'X-COMP OF SURF & BL WIND STRESS N/M2',
         'm01s03i220': 'Y-COMP OF SURF & BL WIND STRESS N/M2',
         'm01s03i222': 'B.LAYER TOTAL MOISTURE FLUXS KG/M2/S',
         'm01s03i225': '10 METRE WIND U-COMP B GRID',
         'm01s03i226': '10 METRE WIND V-COMP B GRID',
         'm01s03i234': 'SURFACE LATENT HEAT FLUX W/M2',
         'm01s03i236': 'TEMPERATURE AT 1.5M',
         'm01s03i241': 'TOTAL SURF MOIST FLUX PER TIMESTEP',
         'm01s03i245': 'RELATIVE HUMIDITY AT 1.5M',
         'm01s03i281': 'VIS AT 1.5M  (incl precip)',
         'm01s03i290': 'SURFACE SENSIBLE HEAT FLUX ON TILES',
         'm01s03i316': 'SURFACE TEMP ON TILES K',
         'm01s03i321': 'CANOPY WATER ON TILES KG/M2',
         'm01s03i328': '1.5M TEMPERATURE OVER TILES',
         'm01s03i476': 'COMBINED BOUNDARY LAYER TYPE',
         'm01s04i201': 'LARGE SCALE RAIN AMOUNT KG/M2/TS',
         'm01s08i225': 'DEEP SOIL TEMP. AFTER HYDROLOGY DEGK',
         'm01s09i203': 'LOW CLOUD AMOUNT',
         'm01s09i204': 'MEDIUM CLOUD AMOUNT',
         'm01s09i205': 'HIGH CLOUD AMOUNT',
         'm01s09i217': 'TOTAL CLOUD AMOUNT MAX/RANDOM OVERLP',
         'm01s09i229': 'RELATIVE HUMIDITY AFTER MAIN CLOUD',
         'm01s16i004': 'TEMPERATURE ON THETA LEVELS',
         'm01s16i202': 'GEOPOTENTIAL HEIGHT ON P LEV/P GRID',
         'm01s16i222': 'PRESSURE AT MEAN SEA LEVEL',
         'm01s01i235': 'TOTAL DOWNWARD SURFACE SW FLUX',
         'm01s01i201': 'NET DOWN SURFACE SW FLUX: SW TS ONLY !!!',
         'm01s02i207': 'DOWNWARD LW RAD FLUX: SURFACE',
         'm01s02i201': 'NET DOWN SURFACE LW RAD FLUX !!!'}
stash_codes = stash.keys()

# for finding files: stash codes
# kup: down then star
# wind: u then v
variables = {'Tair': 'm01s16i004',
             'RH': 'm01s09i229',
             'Press': 'm01s00i408',
             'wind': ['m01s00i002', 'm01s00i003'],
             'kdown': 'm01s01i235',
             'ldown': 'm01s02i207',
             'kup': ['m01s01i235', 'm01s01i201'],
             'RH_q': ['m01s16i004', 'm01s00i408', 'm01s00i010'],
             'H': 'm01s03i217',
             'LE': 'm01s03i234',
             'BL_H': 'm01s03i216'}

# dict to help with adding new variables to Model Eval
# still will have to make edits to sort_obs and sort_models when adding a new variable
# order is:
# 1. label for plot axis (variable name and unit as string) -- wind has two for speed and direction (in that order)
# 2. either 'levels' or 'surface', dependant on if the variable is at the surface or on model levels. This is to help
# for the legend in time series plots
# 3. unit string only (used within moving stats)
# 4. hit rate thresholds as a list, [harsh, kind]
# 5. Histogram bin size
# 6. y limit for the ensemble metrics

variable_info = {'Tair': ['Air Temperature ($^{\circ}$C)', 'levels', '$^{\circ}$C', [0.5, 1.0], 0.5, [0, 25]],

                 'RH': ['Relative Humidity (%)', 'levels', '%', [1.0, 5.0], 2.0, []],

                 'RH_q': ['Relative Humidity (%)', 'levels', '%', [1.0, 5.0], 2.0, [0, 100]],

                 'Press': ['Pressure (hPa)', 'levels', 'hPa', [1.0, 2.25], 2.0, []],

                 'wind': [['Wind Speed (m s$^{-1}$)', 'Wind Direction ($^{\circ}$)'], 'levels', 'm s$^{-1}$',
                          [0.5, 1.0], 2.0, []],

                 'kdown': ['Incoming Shortwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 10,
                           [0, 400]],

                 'ldown': ['Incoming Longwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],

                 'lup': ['Outgoing Longwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],

                 'kup': ['Outgoing Shortwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],

                 'netallwave': ['Net All-Wave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],

                 'H': ['Sensible Heat Flux (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [25, 80], 10, [-50, 300]],

                 'LE': ['Latent Heat Flux (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [5, 20], 10, [-10, 50]],

                 'CT2': ['CT2'],  # Added for scintillometry eval

                 'X_c': ['X_c'],  # Added for scintillometry eval

                 'Y_c': ['Y_c'],  # Added for scintillometry eval

                 'X_c, Y_c': ['X_c, Y_c'],  # Added for scintillometry eval

                 'sd_v': ['sd_v'],  # Added for scintillometry eval
                 'L': ['L'],  # Added for scintillometry eval
                 'ustar': ['ustar'],  # Added for scintillometry eval
                 'PAR_W': ['PAR'],  # Added for kdown allignment tests
                 'BL_H': ['BL Heat Flux (W m$^{-2}$)', 'levels', 'W m$^{-2}$', [25, 80], 10, [-50, 300]]}

# calculated from notebooks/surface_altitudes/lon_ukv_surface_altitudes.ipynb
# stash m01s00i033
UKV_site_altitudes = {'Heathrow': 26.084702,
                      'LON_BCT': 25.500525,
                      'LON_BFCL': 25.500525,
                      'LON_BGH': 17.123268,
                      'LON_BTT': 43.288658,
                      'LON_IML': 29.193649,
                      'LON_IMU': 29.193649,
                      'LON_KSSW': 26.755775,
                      'LON_MR': 43.288658,
                      'LON_NK': 28.70874,
                      'LON_RGS': 19.805748,
                      'LON_SWT': 3.0381837,
                      'Reading': 43.790215}

LON_site_altitudes = {'Heathrow': 22.805416107177734,
                      'LON_BCT': 28.072063446044922,
                      'LON_BFCL': 29.131160736083984,
                      'LON_BGH': 29.131160736083984,
                      'LON_BTT': 35.290924072265625,
                      'LON_IML': 24.953636169433594,
                      'LON_IMU': 24.953636169433594,
                      'LON_KSSW': 17.655845642089844,
                      'LON_MR': 35.698440551757813,
                      'LON_NK': 25.287059783935547,
                      'LON_RGS': 26.907081604003906,
                      'LON_SWT': 6.5159897804260254,
                      'Reading': 62.51922607421875}

# obs_hasl = {'SWT_BLS': 54.,
#             'SWT_CL31': 44.5,
#             'SWT_CNR1_LASMkII': 44.,
#             'IMU': 91.,
#             'IMU_CSAT3_Li7500': 72.1,
#             'RGS': 28.1,
#             'MR': 31.5,
#             'NK': 27.,
#             'BTT': 190.,
#             'KSSW': 52.9,
#             'KSSW_CSAT3_Li7500': 42.,
#             'KSSW_CT25K': 47.6,
#             'BCT': 145.,
#             'BFCL': 21.,
#             'BGH': 49.,
#             'IML': 25.5}

# z0 and zd calculated in UMEP, using the McDonald 1998 method, and using a source area of 500 m.
obs_z0_macdonald = {'BCT': 1.664,
                    'BFCL': 1.368,
                    'BGH': 1.436,
                    'BTT': 1.147,
                    'IML': 0.862,
                    'IMU': 0.887,
                    'KSSW': 1.811,
                    'MR': 1.208,
                    'NK': 1.001,
                    'RGS': 2.084,
                    'SWT': 1.073}
obs_zd_macdonald = {'BCT': 16.874,
                    'BFCL': 16.376,
                    'BGH': 18.966,
                    'BTT': 13.759,
                    'IML': 9.386,
                    'IMU': 9.367,
                    'KSSW': 13.238,
                    'MR': 9.783,
                    'NK': 5.321,
                    'RGS': 8.821,
                    'SWT': 5.584}

# [lat, lon] in WGS84
# used for sunrise/ sunset lines in kdown plots
# denise_testsite -- to check if the grid next to KSSW is similar
site_location = {'BCT': [-0.092951, 51.520559],
                 'BFCL': [-0.094398, 51.520532],
                 'BGH': [-0.093295, 51.518777],
                 'BTT': [-0.138843, 51.521454],
                 'IML': [-0.106186, 51.526055],
                 'IMU': [-0.106086, 51.526148],
                 'KSSW': [-0.116722, 51.511794],
                 'MR': [-0.154566, 51.52253],
                 'NK': [-0.2134, 51.521055],
                 'RGS': [-0.17492, 51.501517],
                 'SWT': [-0.091059, 51.487765],
                 'denise_testsite': [-0.1278034, 51.513083],
                 'denise_testsite2': [-0.1046114, 51.5129082]}

Qf = {'January': 25.1447,
      'February': 23.4529,
      'March': 24.6175,
      'April': 20.7802,
      'May': 18.8677,
      'June': 18.1567,
      'July': 17.1881,
      'August': 16.6732,
      'September': 18.5490,
      'October': 20.7435,
      'November': 22.9870,
      'December': 26.1500}

# lat and lon of old file format 3x3 grids
nine_grids = {
    'BTT': [[[51.51391602, 51.51348114, 51.51304626],
             [51.5274086, 51.52697372, 51.52653503],
             [51.54090118, 51.54046631, 51.54002762]],
            [[359.82943726, 359.85092163, 359.87249756],
             [359.83001709, 359.85159302, 359.87322998],
             [359.83078003, 359.85244751, 359.87387085]]],

    'BCT':
        [[[51.51259232, 51.51214981, 51.51169586],
          [51.5260849, 51.52563858, 51.52518463],
          [51.5395813, 51.53913116, 51.53867722]],
         [[359.89440918, 359.915802, 359.93743896],
          [359.89498901, 359.91653442, 359.93823242],
          [359.89581299, 359.9173584, 359.93911743]]],

    'BFCL':
        [[[51.51259232, 51.51214981, 51.51169586],
          [51.5260849, 51.52563858, 51.52518463],
          [51.5395813, 51.53913116, 51.53867722]],
         [[359.89440918, 359.915802, 359.93743896],
          [359.89498901, 359.91653442, 359.93823242],
          [359.89581299, 359.9173584, 359.93911743]]],

    'BGH':
        [[[51.49909973, 51.49865723, 51.49820328],
          [51.51259232, 51.51214981, 51.51169586],
          [51.5260849, 51.52563858, 51.52518463]],
         [[359.89367676, 359.91525269, 359.93685913],
          [359.89440918, 359.915802, 359.93743896],
          [359.89498901, 359.91653442, 359.93823242]]],

    'IML':
        [[[51.51304626, 51.51259232, 51.51214981],
          [51.52653503, 51.5260849, 51.52563858],
          [51.54002762, 51.5395813, 51.53913116]],
         [[359.87249756, 359.89440918, 359.915802],
          [359.87322998, 359.89498901, 359.91653442],
          [359.87387085, 359.89581299, 359.9173584]]],

    'IMU':
        [[[51.51304626, 51.51259232, 51.51214981],
          [51.52653503, 51.5260849, 51.52563858],
          [51.54002762, 51.5395813, 51.53913116]],
         [[359.87249756, 359.89440918, 359.915802],
          [359.87322998, 359.89498901, 359.91653442],
          [359.87387085, 359.89581299, 359.9173584]]],

    'MR':
        [[[51.51391602, 51.51348114, 51.51304626],
          [51.5274086, 51.52697372, 51.52653503],
          [51.54090118, 51.54046631, 51.54002762]],
         [[359.82943726, 359.85092163, 359.87249756],
          [359.83001709, 359.85159302, 359.87322998],
          [359.83078003, 359.85244751, 359.87387085]]],

    'NK':
        [[[51.5017128, 51.50128937, 51.50086212],
          [51.51520538, 51.51478195, 51.51435471],
          [51.52869797, 51.52827454, 51.52784729]],
         [[359.7635498, 359.7850647, 359.80673218],
          [359.76434326, 359.78585815, 359.80764771],
          [359.76495361, 359.78643799, 359.80807495]]],

    'RGS':
        [[[51.48736954, 51.48693085, 51.48649979],
          [51.50086212, 51.50042725, 51.49999237],
          [51.51435471, 51.51391602, 51.51348114]],
         [[359.80612183, 359.82809448, 359.84936523],
          [359.80673218, 359.82861328, 359.85018921],
          [359.80764771, 359.82943726, 359.85092163]]],

    'KSSW':
        [[[51.49955368, 51.49909973, 51.49865723],
          [51.51304626, 51.51259232, 51.51214981],
          [51.52653503, 51.5260849, 51.52563858]],
         [[359.87191772, 359.89367676, 359.91525269],
          [359.87249756, 359.89440918, 359.915802],
          [359.87322998, 359.89498901, 359.91653442]]],

    'SWT':
        [[[51.47212334, 51.47167429, 51.47122121],
          [51.48561591, 51.48516673, 51.4847135],
          [51.49910847, 51.49865916, 51.49820579]],
         [[359.89209097, 359.91374853, 359.93540566],
          [359.89280894, 359.91447299, 359.93613661],
          [359.89352734, 359.91519788, 359.93686799]]],

    'SWINDON':
        [[[51.5846, 51.5846, 51.5846],
          [51.5846, 51.5846, 51.5846],
          [51.5846, 51.5846, 51.5846]],
         [[358.2019, 358.2019, 358.2019],
          [358.2019, 358.2019, 358.2019],
          [358.2019, 358.2019, 358.2019]]]}

grid_dict = {1: ['MR A', 'BTT A'],
             2: ['MR B', 'BTT B'],
             3: ['MR C', 'BTT C', 'IMU A', 'IML A'],
             4: ['IMU B', 'IML B', 'BFCL A', 'BCT A'],
             5: ['IMU C', 'IML C', 'BFCL B', 'BCT B'],
             6: ['BFCL C', 'BCT C'],
             7: ['NK A'],
             8: ['NK B'],
             9: ['NK C'],
             10: ['MR D', 'BTT D'],
             11: ['MR E', 'BTT E', 'KSSW A'],
             12: ['MR F', 'BTT F', 'IMU D', 'IML D', 'KSSW B'],
             13: ['IMU E', 'IML E', 'BFCL D', 'BCT D', 'BGH A', 'KSSW C'],
             14: ['IMU F', 'IML F', 'BFCL E', 'BCT E', 'BGH B'],
             15: ['BFCL F', 'BCT F', 'BGH C'],
             16: ['NK D'],
             17: ['NK E'],
             18: ['RGS A', 'NK F'],
             19: ['MR G', 'BTT G', 'RGS B'],
             20: ['MR H', 'BTT H', 'RGS C', 'KSSW D'],
             21: ['MR I', 'BTT I', 'IMU G', 'IML G', 'KSSW E'],
             22: ['IMU H', 'IML H', 'BFCL G', 'BCT G', 'BGH D', 'KSSW F'],
             23: ['IMU I', 'IML I', 'BFCL H', 'BCT H', 'BGH E'],
             24: ['BFCL I', 'BCT I', 'BGH F'],
             25: ['NK G'],
             26: ['NK H'],
             27: ['RGS D', 'NK I'],
             28: ['RGS E'],
             29: ['RGS F', 'KSSW G'],
             30: ['KSSW H'],
             31: ['BGH G', 'KSSW I', 'SWT A'],
             32: ['BGH H', 'SWT B'],
             33: ['BGH I', 'SWT C'],
             34: ['RGS G'],
             35: ['RGS H'],
             36: ['RGS I'],
             37: ['SWT D'],
             38: ['SWT E'],
             39: ['SWT F'],
             40: ['SWT G'],
             41: ['SWT H'],
             42: ['SWT I']
             }

grid_dict_colours = {1: 'dimgrey',
                     2: 'darkgrey',
                     3: 'lightgrey',
                     4: 'rosybrown',
                     5: 'brown',
                     6: 'darkred',
                     7: 'salmon',
                     8: 'coral',
                     9: 'sienna',
                     10: 'saddlebrown',
                     11: 'peru',
                     12: 'darkorange',
                     13: 'tan',
                     14: 'wheat',
                     15: 'darkgoldenrod',
                     16: 'gold',
                     17: 'palegoldenrod',
                     18: 'olive',
                     19: 'yellowgreen',
                     20: 'chartreuse',
                     21: 'darkseagreen',
                     22: 'pink',
                     23: 'green',
                     24: 'mediumseagreen',
                     25: 'mediumspringgreen',
                     26: 'turquoise',
                     27: 'darkslategrey',
                     28: 'darkcyan',
                     29: 'darkturquoise',
                     30: 'lightblue',
                     31: 'lightskyblue',
                     32: 'dodgerblue',
                     33: 'slategrey',
                     34: 'royalblue',
                     35: 'midnightblue',
                     36: 'mediumblue',
                     37: 'darkslateblue',
                     38: 'rebeccapurple',
                     39: 'darkorchid',
                     40: 'purple',
                     41: 'magenta',
                     42: 'deeppink',
                     'Average': 'red',
                     'WAverage': 'blue'
                     }

scint_3_b_3_upwind = {12: [10, 11, 12, 19, 20, 21, 28, 29, 30]}
