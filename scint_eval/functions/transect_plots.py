import scintools as sct
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scintools.utils import path_weight


def plot_transects(path_11, pt_11,
                   path_12, pt_12,
                   path_13, pt_13,
                   path_14, pt_14,
                   path_15, pt_15,
                   hori_res,
                   pw_fun=sct.path_weight.bessel_approx):
    # which path is the longest?
    path_list = [path_11, path_12, path_13, path_14, path_15]
    path_length_list = [i.path_length() for i in path_list]
    x_lim_max = max(path_length_list)

    # which path has the highest element
    transect_list = [pt_11, pt_12, pt_13, pt_14, pt_15]
    transect_max_list = [max(i.gdf["z_asl_max_bdsm"]) for i in transect_list]
    y_lim_max = max(transect_max_list)

    fig = plt.figure(constrained_layout=True, figsize=(10, 14))
    spec = gridspec.GridSpec(ncols=1, nrows=5)

    ax1 = fig.add_subplot(spec[0])
    ax2 = fig.add_subplot(spec[1])
    ax3 = fig.add_subplot(spec[2])
    ax4 = fig.add_subplot(spec[3])
    ax5 = fig.add_subplot(spec[4])

    # plot the path weighting curve

    path_weight_df_11 = path_weight.path_weight(fx=pw_fun, n_x=pt_11.gdf.shape[0])
    path_weight_df_12 = path_weight.path_weight(fx=pw_fun, n_x=pt_12.gdf.shape[0])
    path_weight_df_13 = path_weight.path_weight(fx=pw_fun, n_x=pt_13.gdf.shape[0])
    path_weight_df_14 = path_weight.path_weight(fx=pw_fun, n_x=pt_14.gdf.shape[0])
    path_weight_df_15 = path_weight.path_weight(fx=pw_fun, n_x=pt_15.gdf.shape[0])

    ax1_t = ax1.twinx()
    ax2_t = ax2.twinx()
    ax3_t = ax3.twinx()
    ax4_t = ax4.twinx()
    ax5_t = ax5.twinx()

    pw_line_11 = ax1_t.plot(pt_11.gdf.index * pt_11.point_res,
                            path_weight_df_11["path_weight"], color="blue", linestyle='--',
                            label='Path weighting function', alpha=0.5)
    pw_line_12 = ax2_t.plot(pt_12.gdf.index * pt_12.point_res,
                            path_weight_df_12["path_weight"], color="blue", linestyle='--',
                            label='Path weighting function', alpha=0.5)
    pw_line_13 = ax3_t.plot(pt_13.gdf.index * pt_13.point_res,
                            path_weight_df_13["path_weight"], color="blue", linestyle='--',
                            label='Path weighting function', alpha=0.5)
    pw_line_14 = ax4_t.plot(pt_14.gdf.index * pt_14.point_res,
                            path_weight_df_14["path_weight"], color="blue", linestyle='--',
                            label='Path weighting function', alpha=0.5)
    pw_line_15 = ax5_t.plot(pt_15.gdf.index * pt_15.point_res,
                            path_weight_df_15["path_weight"], color="blue", linestyle='--',
                            label='Path weighting function', alpha=0.5)

    ax1.spines['right'].set_color('blue')
    ax1_t.spines['right'].set_color('blue')
    ax1_t.yaxis.label.set_color('blue')
    ax1_t.tick_params(axis='y', colors='blue')

    ax2.spines['right'].set_color('blue')
    ax2_t.spines['right'].set_color('blue')
    ax2_t.yaxis.label.set_color('blue')
    ax2_t.tick_params(axis='y', colors='blue')

    ax3.spines['right'].set_color('blue')
    ax3_t.spines['right'].set_color('blue')
    ax3_t.yaxis.label.set_color('blue')
    ax3_t.tick_params(axis='y', colors='blue')

    ax4.spines['right'].set_color('blue')
    ax4_t.spines['right'].set_color('blue')
    ax4_t.yaxis.label.set_color('blue')
    ax4_t.tick_params(axis='y', colors='blue')

    ax5.spines['right'].set_color('blue')
    ax5_t.spines['right'].set_color('blue')
    ax5_t.yaxis.label.set_color('blue')
    ax5_t.tick_params(axis='y', colors='blue')

    ax1_t.set_ylim(0, 1)
    ax2_t.set_ylim(0, 1)
    ax3_t.set_ylim(0, 1)
    ax4_t.set_ylim(0, 1)
    ax5_t.set_ylim(0, 1)

    # plt.setp(ax1_t.get_yticklabels()[0], visible=False)
    plt.setp(ax2_t.get_yticklabels()[-1], visible=False)
    plt.setp(ax3_t.get_yticklabels()[-1], visible=False)
    plt.setp(ax4_t.get_yticklabels()[-1], visible=False)
    plt.setp(ax5_t.get_yticklabels()[-1], visible=False)

    ax3_t.set_ylabel("Path Weighting")

    # bld_bar_11 = ax1.bar(pt_11.gdf.index * pt_11.point_res, pt_11.gdf["z_asl_max_bdsm"], hori_res, color='grey')
    # # bld_line_11 = ax1.plot(pt_11.gdf.index * pt_11.point_res, pt_11.gdf["z_asl_max"], color='blue',
    # #                        label='Building heights')
    # dem_bar_11 = ax1.bar(pt_11.gdf.index * pt_11.point_res, pt_11.gdf["z_asl_max_dem"], hori_res, color='brown')

    bld_bar_11 = ax1.bar(pt_11.gdf.index * pt_11.point_res, pt_11.gdf["z_asl_max_bdsm"] - pt_11.gdf["z_asl_max_dem"],
                         hori_res, color='grey')
    dem_bar_11 = ax1.bar(pt_11.gdf.index * pt_11.point_res, pt_11.gdf["z_asl_max_dem"] * -1, hori_res, color='sienna')

    # bld_bar_12 = ax2.bar(pt_12.gdf.index * pt_12.point_res, pt_12.gdf["z_asl_max_bdsm"], hori_res, color='grey')
    # # bld_line_12 = ax2.plot(pt_12.gdf.index * pt_12.point_res, pt_12.gdf["z_asl_max"], color='blue',
    # #                        label='Building heights')
    bld_bar_12 = ax2.bar(pt_12.gdf.index * pt_12.point_res, pt_12.gdf["z_asl_max_bdsm"] - pt_12.gdf["z_asl_max_dem"],
                         hori_res, color='grey')
    dem_bar_12 = ax2.bar(pt_12.gdf.index * pt_12.point_res, pt_12.gdf["z_asl_max_dem"] * -1, hori_res, color='sienna')

    # bld_bar_13 = ax3.bar(pt_13.gdf.index * pt_13.point_res, pt_13.gdf["z_asl_max_bdsm"], hori_res, color='grey')
    # # bld_line_13 = ax3.plot(pt_13.gdf.index * pt_13.point_res, pt_13.gdf["z_asl_max"], color='blue',
    # #                        label='Building heights')
    bld_bar_13 = ax3.bar(pt_13.gdf.index * pt_13.point_res, pt_13.gdf["z_asl_max_bdsm"] - pt_13.gdf["z_asl_max_dem"],
                         hori_res, color='grey')
    dem_bar_13 = ax3.bar(pt_13.gdf.index * pt_13.point_res, pt_13.gdf["z_asl_max_dem"] * -1, hori_res, color='sienna')

    # bld_bar_14 = ax4.bar(pt_14.gdf.index * pt_14.point_res, pt_14.gdf["z_asl_max_bdsm"], hori_res, color='grey')
    # # bld_line_14 = ax4.plot(pt_14.gdf.index * pt_14.point_res, pt_14.gdf["z_asl_max"], color='blue',
    # #                        label='Building heights')
    bld_bar_14 = ax4.bar(pt_14.gdf.index * pt_14.point_res, pt_14.gdf["z_asl_max_bdsm"] - pt_14.gdf["z_asl_max_dem"],
                         hori_res, color='grey')
    dem_bar_14 = ax4.bar(pt_14.gdf.index * pt_14.point_res, pt_14.gdf["z_asl_max_dem"] * -1, hori_res, color='sienna')

    # bld_bar_15 = ax5.bar(pt_15.gdf.index * pt_15.point_res, pt_15.gdf["z_asl_max_bdsm"], hori_res, color='grey')
    # # bld_line_15 = ax5.plot(pt_15.gdf.index * pt_15.point_res, pt_15.gdf["z_asl_max"], color='blue',
    # #                        label='Building heights')
    bld_bar_15 = ax5.bar(pt_15.gdf.index * pt_15.point_res, pt_15.gdf["z_asl_max_bdsm"] - pt_15.gdf["z_asl_max_dem"],
                         hori_res, color='grey')
    dem_bar_15 = ax5.bar(pt_15.gdf.index * pt_15.point_res, pt_15.gdf["z_asl_max_dem"] * -1, hori_res, color='sienna')

    # plot the path
    path_line_11 = ax1.plot(pt_11.gdf.path_length_m, pt_11.gdf["path_height_asl"], color='blue',
                            label='LAS path')

    path_line_12 = ax2.plot(pt_12.gdf.path_length_m, pt_12.gdf["path_height_asl"], color='red',
                            label='LAS path')

    path_line_13 = ax3.plot(pt_13.gdf.path_length_m, pt_13.gdf["path_height_asl"], color='green',
                            label='LAS path')

    path_line_14 = ax4.plot(pt_14.gdf.path_length_m, pt_14.gdf["path_height_asl"], color='orange',
                            label='LAS path')

    path_line_15 = ax5.plot(pt_15.gdf.path_length_m, pt_15.gdf["path_height_asl"], color='magenta',
                            label='LAS path')

    ax3.set_ylabel('Height (m)')

    ax1.set_xticks([])
    ax2.set_xticks([])
    ax3.set_xticks([])
    ax4.set_xticks([])

    ax1.set_xlim(0 - 10, x_lim_max + 10)
    ax2.set_xlim(0 - 10, x_lim_max + 10)
    ax3.set_xlim(0 - 10, x_lim_max + 10)
    ax4.set_xlim(0 - 10, x_lim_max + 10)
    ax5.set_xlim(0 - 10, x_lim_max + 10)

    # ax1.set_ylim(0, y_lim_max + 10)
    # ax2.set_ylim(0, y_lim_max + 10)
    # ax3.set_ylim(0, y_lim_max + 10)
    # ax4.set_ylim(0, y_lim_max + 10)
    # ax5.set_ylim(0, y_lim_max + 10)

    # add effective beam height label
    ebh_11 = pt_11.effective_beam_height()
    ebh_12 = pt_12.effective_beam_height()
    ebh_13 = pt_13.effective_beam_height()
    ebh_14 = pt_14.effective_beam_height()
    ebh_15 = pt_15.effective_beam_height()

    plt.text(0.9, 0.9,
             str(path_11.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_11.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax1.transAxes)

    plt.text(0.9, 0.9,
             str(path_12.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_12.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax2.transAxes)

    plt.text(0.9, 0.9,
             str(path_13.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_13.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax3.transAxes)

    plt.text(0.9, 0.9,
             str(path_14.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_14.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax4.transAxes)

    plt.text(0.9, 0.9,
             str(path_15.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_15.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax5.transAxes)

    plt.text(0.9, 0.8, '$z_{fb}$ = %d.2 m agl' % ebh_11, horizontalalignment='center', transform=ax1.transAxes)
    plt.text(0.9, 0.8, '$z_{fb}$ = %d.2 m agl' % ebh_12, horizontalalignment='center', transform=ax2.transAxes)
    plt.text(0.9, 0.8, '$z_{fb}$ = %d.2 m agl' % ebh_13, horizontalalignment='center', transform=ax3.transAxes)
    plt.text(0.9, 0.8, '$z_{fb}$ = %d.2 m agl' % ebh_14, horizontalalignment='center', transform=ax4.transAxes)
    plt.text(0.9, 0.8, '$z_{fb}$ = %d.2 m agl' % ebh_15, horizontalalignment='center', transform=ax5.transAxes)

    # added these three lines
    # lns = bld_bar_11 + path_line_11 + pw_line_11
    # labs = [l.get_label() for l in lns]
    # ax1.legend(lns, labs, frameon=False, prop={'size': 8})
    # ax1.legend(frameon=False)

    ax5.set_xlabel('Horizontal distance (m)')

    plt.subplots_adjust(wspace=0, hspace=0)

    plt.savefig('C:/Users/beths/OneDrive - University of Reading/Paper 2/Plan/path_transect.png', bbox_inches='tight')

    print('end')


def plot_2_transects(path_12, pt_12,
                     path_15, pt_15,
                     hori_res,
                     pw_fun=sct.path_weight.bessel_approx):
    # which path is the longest?
    path_list = [path_12, path_15]
    path_length_list = [i.path_length() for i in path_list]
    x_lim_max = max(path_length_list)

    # which path has the highest element
    transect_list = [pt_12, pt_15]
    transect_max_list = [max(i.gdf["z_asl_max_bdsm"]) for i in transect_list]
    y_lim_max = max(transect_max_list)

    fig = plt.figure(constrained_layout=True, figsize=(10, 6))
    spec = gridspec.GridSpec(ncols=1, nrows=2)

    ax1 = fig.add_subplot(spec[0])
    ax2 = fig.add_subplot(spec[1])

    # plot the path weighting curve
    path_weight_df_12 = path_weight.path_weight(fx=pw_fun, n_x=pt_12.gdf.shape[0])
    path_weight_df_15 = path_weight.path_weight(fx=pw_fun, n_x=pt_15.gdf.shape[0])

    ax1_t = ax1.twinx()
    ax2_t = ax2.twinx()

    pw_line_12 = ax1_t.plot(pt_12.gdf.index * pt_12.point_res,
                            path_weight_df_12["path_weight"], color="magenta", linestyle='--',
                            label='Path weighting function', alpha=0.5)
    pw_line_15 = ax2_t.plot(pt_15.gdf.index * pt_15.point_res,
                            path_weight_df_15["path_weight"], color="magenta", linestyle='--',
                            label='Path weighting function', alpha=0.5)

    ax1.spines['right'].set_color('magenta')
    ax1_t.spines['right'].set_color('magenta')
    ax1_t.yaxis.label.set_color('magenta')
    ax1_t.tick_params(axis='y', colors='magenta')

    ax2.spines['right'].set_color('magenta')
    ax2_t.spines['right'].set_color('magenta')
    ax2_t.yaxis.label.set_color('magenta')
    ax2_t.tick_params(axis='y', colors='magenta')

    plt.setp(ax2_t.get_yticklabels()[-1], visible=False)

    bld_bar_12 = ax1.bar(pt_12.gdf.index * pt_12.point_res, pt_12.gdf["z_asl_max_bdsm"],
                         hori_res, color='grey')
    dem_bar_12 = ax1.bar(pt_12.gdf.index * pt_12.point_res, pt_12.gdf["z_asl_max_dem"], hori_res, color='sienna')

    bld_bar_15 = ax2.bar(pt_15.gdf.index * pt_15.point_res, pt_15.gdf["z_asl_max_bdsm"],
                         hori_res, color='grey')
    dem_bar_15 = ax2.bar(pt_15.gdf.index * pt_15.point_res, pt_15.gdf["z_asl_max_dem"], hori_res, color='sienna')

    # plot the path
    path_line_12 = ax1.plot(pt_12.gdf.path_length_m, pt_12.gdf["path_height_asl"], color='blue',
                            label='LAS path')

    path_line_15 = ax2.plot(pt_15.gdf.path_length_m, pt_15.gdf["path_height_asl"], color='red',
                            label='LAS path')

    ax1.set_xticks([])

    ax1.set_xlim(0, x_lim_max)
    ax2.set_xlim(0, x_lim_max)


    ax1.set_ylim(0, y_lim_max+5)
    ax2.set_ylim(0, y_lim_max+5)

    # add effective beam height label
    ebh_12 = pt_12.effective_beam_height()
    ebh_15 = pt_15.effective_beam_height()

    plt.text(0.94, 0.94,
             str(path_12.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_12.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax1.transAxes, color='blue')

    plt.text(0.94, 0.94,
             str(path_15.pair_id.split('_')[0] + r' $\rightarrow$ ' + path_15.pair_id.split('_')[1]),
             horizontalalignment='center', transform=ax2.transAxes, color='red')

    plt.text(0.5, 0.6, '$z_{fb}$ = %d.2 m agl' % ebh_12, horizontalalignment='center', transform=ax1.transAxes,
             color='green')
    plt.text(0.5, 0.2, '$z_{fb}$ = %d.2 m agl' % ebh_15, horizontalalignment='center', transform=ax2.transAxes,
             color='green')

    ax1.plot(pt_12.gdf.path_length_m, ebh_12 + pt_12.gdf["z_asl_max_dem"], color='green', linestyle=':')
    ax2.plot(pt_15.gdf.path_length_m, ebh_15 + pt_15.gdf["z_asl_max_dem"], color='green', linestyle=':')

    ax2.set_xlabel('Horizontal distance (m)')

    plt.subplots_adjust(wspace=0, hspace=0)

    fig.text(0.075, 0.5, 'Height asl (m)', va='center', rotation='vertical')
    fig.text(0.94, 0.5, 'Path Weighting', va='center', rotation='vertical', color='magenta')

    plt.savefig('C:/Users/beths/OneDrive - University of Reading/Paper 2/Plan/path_transect.png', bbox_inches='tight')

    print('end')


########################################################################################################################
hori_res = 10

# path definition

# # path 11 - BTT -> BCT
# path_11 = sct.ScintillometerPair(x=[282251.14, 285440.6056],
#                                  y=[5712486.47, 5712253.017],
#                                  z_asl=[180, 142],
#                                  pair_id='BTT_BCT',
#                                  crs='epsg:32631')

# path 12 - BCT -> IMU
path_12 = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                 y=[5712253.017, 5712935.032],
                                 z_asl=[142, 88],
                                 pair_id='BCT_IMU',
                                 crs='epsg:32631')

# # path 13 - IMU -> BTT
# path_13 = sct.ScintillometerPair(x=[284562.3107, 282251.14],
#                                  y=[5712935.032, 5712486.47],
#                                  z_asl=[88, 180],
#                                  pair_id='IMU_BTT',
#                                  crs='epsg:32631')

# # path 14 - IMU -> SWT
# path_14 = sct.ScintillometerPair(x=[284562.3107, 285407],
#                                  y=[5712935.032, 5708599.83],
#                                  z_asl=[88, 44],
#                                  pair_id='IMU_SWT',
#                                  crs='epsg:32631')

# path 15 - SCT -> SWT
path_15 = sct.ScintillometerPair(x=[284450.1944, 285407],
                                 y=[5708094.734, 5708599.83],
                                 z_asl=[51, 44],
                                 pair_id='SCT_SWT',
                                 crs='epsg:32631')

bdsm_file = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
dem_file = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'

# pt_11 = path_11.path_transect(bdsm_file, dem_file, hori_res)
pt_12 = path_12.path_transect(bdsm_file, dem_file, hori_res)
# pt_13 = path_13.path_transect(bdsm_file, dem_file, hori_res)
# pt_14 = path_14.path_transect(bdsm_file, dem_file, hori_res)
pt_15 = path_15.path_transect(bdsm_file, dem_file, hori_res)

# plot_transects(path_11, pt_11,
#                path_12, pt_12,
#                path_13, pt_13,
#                path_14, pt_14,
#                path_15, pt_15,
#                hori_res)

plot_2_transects(path_12, pt_12,
                 path_15, pt_15,
                 hori_res)

print('end')
