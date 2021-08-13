import netCDF4 as nc
import numpy as np


def retrive_var(file_dict,
                var_names):
    """
    Retrive variable from ncdf file
    :param file_path: sting of ncdf filepath
    :param var_names: LIST of strings; variable names as they appear in ncdf file
    :return: Dict of both time (as array of datetime objects) & variable array
    """

    all_days_vars = {}

    for day in sorted(file_dict.keys()):
        file_path = file_dict[day]

        ncdf_file = nc.Dataset(file_path)

        # reads in observation height
        height_obs = np.array(ncdf_file.variables['z_f'][:], dtype=np.float)

        file_time = ncdf_file.variables['time']
        time_dt = nc.num2date(file_time[:], file_time.units)

        var_dict = {'time': time_dt}
        var_dict['z_f'] = height_obs

        for var_name in var_names:
            file_var = ncdf_file.variables[var_name]
            var_array = np.array(file_var[:], dtype=np.float)
            var_dict[var_name] = var_array

        all_days_vars[day] = var_dict

    return all_days_vars