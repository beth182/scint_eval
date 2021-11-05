import rasterio  # the GEOS-based raster package
import numpy  # the array computation library
import geopandas  # the GEOS-based vector package
import matplotlib.pyplot as plt  # the visualization package
import numpy as np
from rasterio.mask import mask
import pylab
import matplotlib as mpl
# mpl.use('TkAgg')

def SA_grid_percentages(raster_path, save_path, time_string):
    """
    A function to return the percentages from a a scintillometry SA raster file which fall within the UKV grid
    network in Model Eval
    :param raster_path: A path to the raster file
    :return:
    """

    # help from https://pysal.org/scipy2019-intermediate-gds/deterministic/gds2-rasters.html

    raster = rasterio.open(raster_path)
    SA_data = raster.read(1)

    # value of the total values across all of the raster
    total_SA_sum = np.nansum(SA_data)

    # construct the extent: raster.bounds
    # matplotlib and geographic packages like rasterio and geopandas use different ordering conventions for
    # their bounding box information.
    # geographic information systems (bounds): (west, south, north, east)
    # matplotlib (extent): (west, east, south, north)
    # re-arrange the raster.bounds to extent form, expected by matplotlib:
    raster_extent = numpy.asarray(raster.bounds)[[0, 2, 1, 3]]

    # Subsetting the raster
    # To focus the raster down to a grid, we can use the grid data, which we converted into geographic information
    gpkg_dir_path = 'C:/Users/beths/Desktop/LANDING/grid_gpkg_files/'

    # plotting all grids against raster data
    f = plt.figure(figsize=(20, 20))

    # SA_data = np.ma.masked_where(SA_data < (total_SA_sum / 10000), SA_data)
    cmap = mpl.cm.jet
    cmap.set_bad('white', 1.)
    plt.imshow(SA_data, interpolation='none', cmap=cmap, extent=raster_extent)

    # plt.colorbar(im, orientation='horizontal', pad=0.1)

    # makes list to see total value outside loop
    grid_vals = {}

    for i in range(1, 43):

        grid_num = str(i)
        gpkg_file_name = grid_num + '.gpkg'

        gpkg_file = gpkg_dir_path + gpkg_file_name
        grid_gpkg = geopandas.read_file(gpkg_file)

        # bounding box for our grid is the total_bounds of our grid dataframe:
        grid_bbox = grid_gpkg.total_bounds

        # Subsetting raster data
        # takes the coordinates from a bounding box and provides a rasterio.windows.Window object.
        # We can use it directly from our grid_bbox data using *, the unpack operator
        grid_window = raster.window(*grid_bbox)

        # Now, when we read() in our data, we can use this rasterio.windows.Window object to only read
        # the data we want to analyze: that within the bounds of the grid:
        grid_SA_data = raster.read(1, window=grid_window)

        # adding to the all grid plot
        grid_gpkg.boundary.plot(ax=plt.gca(), color='skyblue')

        # Summing the SA data within the grid box
        # implementing zonal statistics using rasterio mask
        grid_geometry = grid_gpkg.geometry

        # try except Value error here because ValueError occurs when the grid has no overlap of raster
        try:
            masked, mask_transform = mask(dataset=raster,
                                          shapes=grid_geometry, crop=True,
                                          all_touched=False,
                                          filled=False)

            # The mask function returns an array with the shape (n_bands, n_rows, n_columns).
            # Thus, when working with a single band, the mask function will output an array that has an 'extra'
            # dimension; the array will be three-dimensional despite the output only having two effective dimensions.
            # So, we must use squeeze() to remove extra dimensions that only have one element
            masked = masked.squeeze()

            # summing the values in this grid
            summed_val = np.nansum(masked)
            # as a percentage of the total raster, and rounded to 4 sig fig.
            grid_sum = round((summed_val / total_SA_sum) * 100, 4)

        except ValueError:
            # traceback.print_exc()
            grid_sum = np.nan

        grid_vals[i] = grid_sum

    calculated_sum_list = []
    for grid in sorted(grid_vals):
        calculated_sum_list.append(grid_vals[grid])

    # sum calculated by adding the sums of all individual grids
    calculated_sum = np.nansum(calculated_sum_list)

    pylab.savefig(save_path + 'raster_grids_' + time_string + '.png', bbox_inches='tight')

    plt.close('all')

    return grid_vals, calculated_sum

# raster_path = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/hourly/applicable_hours/BCT_IMU_65000_2016_142_05.tif'
# save_path = 'D:/Documents/scint_eval/plots/2016142_2016142_H_IMU_12/'
# time_string = 'test'
#
# SA_grid_percentages(raster_path, save_path, time_string)
