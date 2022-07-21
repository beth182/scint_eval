from scint_eval.functions import file_read
from scint_eval.functions import observations
from scint_eval.functions import roughness
from scint_eval.functions import array_retrieval
from scint_eval import look_up

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import datetime as dt
from matplotlib import cm
import matplotlib as mpl

DOYstart = 2016001
DOYstop = 2016100

variable = 'kdown'
obs_level = 'L0'
obs_site = 'KSSW'
instrument = 'CNR4'
sample = '5s'
scint_path = 12

# obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
# csv_path = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/data_avail/categorize_days/all_days.csv'

obs_path = '/storage/basic/micromet/Tier_raw/data/'
csv_path = '/storage/basic/micromet/Tier_processing/rv006011/all_days.csv'

folder_name = str(DOYstart) + '_' + str(DOYstop) + '_' + variable + '_' + obs_site + '_' + str(
    scint_path) + '/'
save_folder = '../plots/' + folder_name

files_obs = file_read.finding_files('new', 'obs', DOYstart, DOYstop, obs_site, '21Z', instrument, sample,
                                    variable, obs_level,
                                    obs_path=obs_path
                                    )

z0zdlist = roughness.roughness_and_displacement(1, 0.8, look_up.obs_z0_macdonald[obs_site],
                                                look_up.obs_zd_macdonald[obs_site])

obs = observations.sort_obs(variable, files_obs, DOYstart, DOYstop, obs_site, z0zdlist, 1,
                            save_folder, sample,
                            instrument)

plt.close('all')

group_obs = [obs[4], obs[2], obs[3], obs[0], obs[1], obs[5]]

obs_time, obs_vals = array_retrieval.retrive_arrays_obs(group_obs)

# get into pandas df

df = pd.DataFrame.from_dict({'time': obs_time, variable: obs_vals})
df = df.set_index('time')

# time starting 15-min average
resample_df = df.resample('15T', closed='right', label='left').mean()

# taking avergages on the hour only
obs_df = resample_df.iloc[np.where(resample_df.index.minute == 0)[0]]

# make negative values 0
obs_df.iloc[np.where(obs_df.kdown <= 0)[0]] = 0

cmap = cm.get_cmap('rainbow')
bounds = np.linspace(obs_df.kdown.min() - 0.00000000001, obs_df.kdown.max(), 10)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(20, 8))

obs_df["x"] = obs_df.index.date
obs_df["y"] = obs_df.index.hour
obs_df.head()
xi = np.linspace(obs_df.index.strftime('%j').astype(int).min(), obs_df.index.strftime('%j').astype(int).max(), 1000)
yi = np.linspace(obs_df.y.min(), obs_df.y.max(), 1000)
zi = griddata((obs_df.index.strftime('%j').astype(int), obs_df.index.hour), obs_df.kdown, (xi[None, :], yi[:, None]),
              method='linear')
ye = ax.contourf(xi, yi, zi, levels=bounds, cmap=cmap, norm=norm, alpha=0.5)
# cb = plt.colorbar(ye, ax=ax)
plt.xlabel('DOY')
plt.ylabel('Hour')

days_df = pd.read_csv(csv_path)
doy_list = sorted(list(days_df.iloc[np.where(days_df.Year == 2016)[0]].DOY))
# doy_list = [50]
mask = np.logical_not(np.isin(obs_df.index.strftime('%j').astype(int), doy_list))
subset = obs_df.copy()
subset[mask] = np.nan

subset["x"] = subset.index.date
subset["y"] = subset.index.hour
subset.head()
xi_subset = np.linspace(subset.index.strftime('%j').astype(int).min(), subset.index.strftime('%j').astype(int).max(),
                        1000)
yi_subset = np.linspace(subset.y.min(), subset.y.max(), 1000)
zi_subset = griddata((subset.index.strftime('%j').astype(int), subset.index.hour), subset.kdown,
                     (xi_subset[None, :], yi_subset[:, None]), method='linear')
yee = ax.contourf(xi_subset, yi_subset, zi_subset, levels=bounds, cmap=cmap, norm=norm)
plt.colorbar(yee, ax=ax)

plt.savefig('../../plots/yee.png', bbox_inches='tight')

plt.show()
