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

DOYstart = 2016001
DOYstop = 2016100


variable = 'kdown'
obs_level = 'L0'
obs_site = 'KSSW'
instrument = 'CNR4'
sample = '5s'
scint_path = 12

folder_name = str(DOYstart) + '_' + str(DOYstop) + '_' + variable + '_' + obs_site + '_' + str(
    scint_path) + '/'
save_folder = '../plots/' + folder_name



files_obs = file_read.finding_files('new', 'obs', DOYstart, DOYstop, obs_site, '21Z', instrument, sample,
                                    variable, obs_level,
                                    obs_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/data/"
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



obs_df["x"] = obs_df.index.date
obs_df["y"] = obs_df.index.hour
obs_df.head()
xi = np.linspace(obs_df.index.strftime('%j').astype(int).min(), obs_df.index.strftime('%j').astype(int).max(), 1000)
yi = np.linspace(obs_df.y.min(), obs_df.y.max(), 1000)
zi = griddata((obs_df.index.strftime('%j').astype(int),obs_df.index.hour),obs_df.kdown,(xi[None,:],yi[:,None]),method='linear')
plt.contourf(xi,yi,zi)
plt.colorbar()
plt.xlabel('DOY')
plt.ylabel('Hour')


plt.show()





print('end')