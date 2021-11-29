# testing the sensitivity of SA model output to SA model inputs

import pandas as pd
import netCDF4 as nc
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib import rcParams
import statsmodels.api as sm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scintools as sct




def SA_sensitivity_scatter():
    """

    :return:
    """

    # read in the SA input csv
    csv_path_142 = 'D:/Documents/scintillometer_footprints/scint_fp/test_outputs/met_inputs_minutes_142.csv'
    csv_path_111 = 'D:/Documents/scintillometer_footprints/scint_fp/test_outputs/met_inputs_minutes_111.csv'
    df_142 = pd.read_csv(csv_path_142)
    df_111 = pd.read_csv(csv_path_111)
    df_142['Unnamed: 0'] = pd.to_datetime(df_142['Unnamed: 0'], format='%Y-%m-%d %H:%M:%S')
    df_111['Unnamed: 0'] = pd.to_datetime(df_111['Unnamed: 0'], format='%d/%m/%Y %H:%M')
    df_142 = df_142.set_index('Unnamed: 0')
    df_111 = df_111.set_index('Unnamed: 0')
    df_142.index = df_142.index.round('1s')
    df_111.index = df_111.index.round('1s')

    # combine both days csv files
    df_csv = pd.concat([df_111, df_142])

    # read in the nc file
    nc_path_142 = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data//2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc"
    nc_path_111 = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data//2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc"

    ncdf_file_142 = nc.Dataset(nc_path_142)
    ncdf_file_111 = nc.Dataset(nc_path_111)
    file_time_142 = ncdf_file_142.variables['time']
    file_time_111 = ncdf_file_111.variables['time']
    time_dt_142 = nc.num2date(file_time_142[:], file_time_142.units)
    time_dt_111 = nc.num2date(file_time_111[:], file_time_111.units)

    extent_142 = ncdf_file_142.variables['sa_area_km2']
    extent_111 = ncdf_file_111.variables['sa_area_km2']

    zf_142 = ncdf_file_142.variables['z_f']
    zf_111 = ncdf_file_111.variables['z_f']

    z0_142 = ncdf_file_142.variables['z_0']
    z0_111 = ncdf_file_111.variables['z_0']

    # construct a pandas df for the nc file
    nc_dict_142 = {'time': time_dt_142, 'extent_nc': extent_142[:], 'z_f_nc': zf_142, 'z_0_nc': z0_142}
    nc_dict_111 = {'time': time_dt_111, 'extent_nc': extent_111[:], 'z_f_nc': zf_111, 'z_0_nc': z0_111}

    nc_df_142 = pd.DataFrame(nc_dict_142)
    nc_df_111 = pd.DataFrame(nc_dict_111)
    nc_df_142 = nc_df_142.set_index('time')
    nc_df_111 = nc_df_111.set_index('time')
    nc_df_142.index = nc_df_142.index.round('1s')
    nc_df_111.index = nc_df_111.index.round('1s')
    nc_df_142 = nc_df_142.dropna()
    nc_df_111 = nc_df_111.dropna()

    nc_df_ten_min_142 = nc_df_142.resample('10T', closed='right', label='right').mean()
    nc_df_ten_min_111 = nc_df_111.resample('10T', closed='right', label='right').mean()

    df_nc = pd.concat([nc_df_ten_min_111, nc_df_ten_min_142])

    # combine df
    df = pd.concat([df_csv, df_nc], axis=1)

    plt.figure(figsize=(15, 15))

    spec = gridspec.GridSpec(ncols=3, nrows=3)

    ax1 = plt.subplot(spec[0])
    ax2 = plt.subplot(spec[1])
    ax3 = plt.subplot(spec[2])
    ax4 = plt.subplot(spec[3])
    ax5 = plt.subplot(spec[4])
    ax6 = plt.subplot(spec[5])
    ax7 = plt.subplot(spec[6])
    ax8 = plt.subplot(spec[7])
    ax9 = plt.subplot(spec[8])

    ax1.scatter(df['ustar'], df['extent_nc'], marker='.', color='blue')
    ax1.set_xlabel('u$^{*}$ (m s$^{-1}$)')
    ax1.set_ylabel('SA area (km$^{2}$)')

    ax2.scatter(df['ustar'], df['z_f_nc'], marker='.', color='blue')
    ax2.set_xlabel('u$^{*}$ (m s$^{-1}$)')
    ax2.set_ylabel('z$_{f}$ (m)')

    ax3.scatter(df['ustar'], df['z_0_nc'], marker='.', color='blue')
    ax3.set_xlabel('u$^{*}$ (m s$^{-1}$)')
    ax3.set_ylabel('z$_{0}$ (m)')

    ax4.scatter(df['sig_v'], df['extent_nc'], marker='.', color='red')
    ax4.set_xlabel('$\sigma$v (m s$^{-1}$)')
    ax4.set_ylabel('SA area (km$^{2}$)')

    ax5.scatter(df['sig_v'], df['z_f_nc'], marker='.', color='red')
    ax5.set_xlabel('$\sigma$v (m s$^{-1}$)')
    ax5.set_ylabel('z$_{f}$ (m)')

    ax6.scatter(df['sig_v'], df['z_0_nc'], marker='.', color='red')
    ax6.set_xlabel('$\sigma$v (m s$^{-1}$)')
    ax6.set_ylabel('z$_{0}$ (m)')

    ax7.scatter(df['wind_direction'], df['extent_nc'], marker='.', color='green')
    ax7.set_xlabel('Wind Direction ($^{\circ}$)')
    ax7.set_ylabel('SA area (km$^{2}$)')

    ax8.scatter(df['wind_direction'], df['z_f_nc'], marker='.', color='green')
    ax8.set_xlabel('Wind Direction ($^{\circ}$)')
    ax8.set_ylabel('z$_{f}$ (m)')

    ax9.scatter(df['wind_direction'], df['z_0_nc'], marker='.', color='green')
    ax9.set_xlabel('Wind Direction ($^{\circ}$)')
    ax9.set_ylabel('z$_{0}$ (m)')

    plt.savefig('C:/Users/beths/OneDrive - University of Reading/Paper 2/Plan/test.png', bbox_inches='tight')

    print('end')


def SA_sensitivity_scatter_origins():
    """

    :return:
    """

    # read in the nc file
    nc_path_142 = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data//2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc"
    nc_path_111 = "//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data//2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc"

    ncdf_file_142 = nc.Dataset(nc_path_142)
    ncdf_file_111 = nc.Dataset(nc_path_111)
    file_time_142 = ncdf_file_142.variables['time']
    file_time_111 = ncdf_file_111.variables['time']
    time_dt_142 = nc.num2date(file_time_142[:], file_time_142.units)
    time_dt_111 = nc.num2date(file_time_111[:], file_time_111.units)

    qh_142 = ncdf_file_142.variables['QH']
    qh_111 = ncdf_file_111.variables['QH']

    wd_142 = ncdf_file_142.variables['wind_direction']
    wd_111 = ncdf_file_111.variables['wind_direction']

    ws_142 = ncdf_file_142.variables['wind_speed']
    ws_111 = ncdf_file_111.variables['wind_speed']

    tair_142 = ncdf_file_142.variables['t_air']
    tair_111 = ncdf_file_111.variables['t_air']

    rh_142 = ncdf_file_142.variables['r_h']
    rh_111 = ncdf_file_111.variables['r_h']

    press_142 = ncdf_file_142.variables['pressure']
    press_111 = ncdf_file_111.variables['pressure']

    qstar_142 = ncdf_file_142.variables['qstar']
    qstar_111 = ncdf_file_111.variables['qstar']

    zf_142 = ncdf_file_142.variables['z_f']
    zf_111 = ncdf_file_111.variables['z_f']

    z0_142 = ncdf_file_142.variables['z_0']
    z0_111 = ncdf_file_111.variables['z_0']

    # construct a pandas df for the nc file
    nc_dict_142 = {'time': time_dt_142, 'QH': qh_142, 'wind_direction': wd_142, 'wind_speed': ws_142, 't_air': tair_142,
                   'r_h': rh_142, 'pressure': press_142, 'qstar': qstar_142,
                   'z_f_nc': zf_142, 'z_0_nc': z0_142}

    nc_dict_111 = {'time': time_dt_111, 'QH': qh_111, 'wind_direction': wd_111, 'wind_speed': ws_111, 't_air': tair_111,
                   'r_h': rh_111, 'pressure': press_111, 'qstar': qstar_111,
                   'z_f_nc': zf_111, 'z_0_nc': z0_111}

    nc_df_142 = pd.DataFrame(nc_dict_142)
    nc_df_111 = pd.DataFrame(nc_dict_111)
    nc_df_142 = nc_df_142.set_index('time')
    nc_df_111 = nc_df_111.set_index('time')
    nc_df_142.index = nc_df_142.index.round('1s')
    nc_df_111.index = nc_df_111.index.round('1s')
    nc_df_142 = nc_df_142.dropna()
    nc_df_111 = nc_df_111.dropna()

    nc_df_ten_min_142 = nc_df_142.resample('10T', closed='right', label='right').mean()
    nc_df_ten_min_111 = nc_df_111.resample('10T', closed='right', label='right').mean()

    df = pd.concat([nc_df_ten_min_111, nc_df_ten_min_142])

    # rcParams.update({'figure.autolayout': True})
    fig = plt.figure(figsize=(15, 15))
    spec = gridspec.GridSpec(ncols=4, nrows=3)

    ax1 = plt.subplot(spec[0])
    ax2 = plt.subplot(spec[1])
    ax3 = plt.subplot(spec[2])
    ax4 = plt.subplot(spec[3])
    ax5 = plt.subplot(spec[4])
    ax6 = plt.subplot(spec[5])
    ax7 = plt.subplot(spec[6])
    ax8 = plt.subplot(spec[7])
    ax9 = plt.subplot(spec[8])
    ax10 = plt.subplot(spec[9])
    ax11 = plt.subplot(spec[10])
    ax12 = plt.subplot(spec[11])


    ax1.scatter(df['wind_direction'], df['z_0_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax1.set_xlabel('Wind Direction ($^{\circ}$)')
    ax1.set_ylabel('z$_{0}$ (m)')
    ax1.set_box_aspect(1)

    ax2.scatter(df['wind_direction'], df['z_f_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax2.set_xlabel('Wind Direction ($^{\circ}$)')
    ax2.set_ylabel('z$_{f}$ (m)')
    ax2.set_box_aspect(1)

    ax3.scatter(df['wind_speed'], df['z_0_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax3.set_xlabel('Wind Speed (m s$^{-1}$)')
    ax3.set_ylabel('z$_{0}$ (m)')
    ax3.set_box_aspect(1)

    ax4.scatter(df['wind_speed'], df['z_f_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax4.set_xlabel('Wind Speed (m s$^{-1}$)')
    ax4.set_ylabel('z$_{f}$ (m)')
    ax4.set_box_aspect(1)

    ax5.scatter(df['t_air'], df['z_0_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax5.set_xlabel('Air Temperature ($^{\circ}$C)')
    ax5.set_ylabel('z$_{0}$ (m)')
    ax5.set_box_aspect(1)

    ax6.scatter(df['t_air'], df['z_f_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax6.set_xlabel('Air Temperature ($^{\circ}$C)')
    ax6.set_ylabel('z$_{f}$ (m)')
    ax6.set_box_aspect(1)

    ax7.scatter(df['r_h'], df['z_0_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax7.set_xlabel('Relative Humidity (%)')
    ax7.set_ylabel('z$_{0}$ (m)')
    ax7.set_box_aspect(1)

    ax8.scatter(df['r_h'], df['z_f_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax8.set_xlabel('Relative Humidity (%)')
    ax8.set_ylabel('z$_{f}$ (m)')
    ax8.set_box_aspect(1)

    ax9.scatter(df['pressure'], df['z_0_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax9.set_xlabel('Pressure (hPa)')
    ax9.set_ylabel('z$_{0}$ (m)')
    ax9.set_box_aspect(1)

    ax10.scatter(df['pressure'], df['z_f_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax10.set_xlabel('Pressure (hPa)')
    ax10.set_ylabel('z$_{f}$ (m)')
    ax10.set_box_aspect(1)

    ax11.scatter(df['qstar'], df['z_0_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax11.set_xlabel('Net All-Wave Radiation (W m$^{-2}$)')
    ax11.set_ylabel('z$_{0}$ (m)')
    ax11.set_box_aspect(1)

    s = ax12.scatter(df['qstar'], df['z_f_nc'], marker='.', c=df['QH'], cmap=plt.cm.rainbow)
    ax12.set_xlabel('Net All-Wave Radiation (W m$^{-2}$)')
    ax12.set_ylabel('z$_{f}$ (m)')
    ax12.set_box_aspect(1)



    plt.subplots_adjust(left=0.05, bottom=0.2, right=0.95, top=0.8, wspace=0.3, hspace=0.27)

    cbar_ax = fig.add_axes([0.95, 0.225, 0.02, 0.145])
    cbar = fig.colorbar(s, cax=cbar_ax)
    cbar.set_label('$Q_{H}$ (W m$^{-2}$)', rotation=270, labelpad=15)

    plt.savefig('C:/Users/beths/OneDrive - University of Reading/Paper 2/Plan/test2.png', bbox_inches='tight')

    print('end')


SA_sensitivity_scatter_origins()
print('end')
