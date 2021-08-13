import pandas as pd
import matplotlib.pyplot as plt
import pylab


def kdown_averages(obs_time, obs_vals, minute_resolution):

    # convert arrays to a df
    df_dict = {'time': obs_time, 'vals': obs_vals}
    df = pd.DataFrame(df_dict)

    df = df.drop_duplicates()
    raw_time = df['time']
    # check that there are no duplicated times in the raw dataframe
    assert len(df[raw_time.isin(raw_time[raw_time.duplicated()])]) == 0

    # construct a string to go into resample denoting the rule
    freq_string = str(minute_resolution) + 'T'

    # resample to minute_resolution
    # time-ending
    # resample_df = df.resample(freq_string, on='time', closed='right', label='right').mean()

    # time starting
    resample_df = df.resample(freq_string, on='time').mean()

    sample_count = df.resample(freq_string, on='time', closed='right', label='right')['vals'].count()
    n_samples = sample_count.rename('n_samples')

    resample_df = pd.concat([resample_df, n_samples], axis=1)

    return resample_df


def compare_samples(obs_time, obs_vals, savestring):


    five_min = kdown_averages(obs_time, obs_vals, 5)
    fifteen_min = kdown_averages(obs_time, obs_vals, 15)
    hour_min = kdown_averages(obs_time, obs_vals, 60)

    plt.figure(figsize=(20, 10))
    plt.scatter(obs_time, obs_vals, marker='o', label='5s')
    plt.scatter(five_min.index, five_min['vals'], marker='.', label='5min')
    plt.scatter(fifteen_min.index, fifteen_min['vals'], marker='p', label='15min')
    plt.scatter(hour_min.index[1:], hour_min['vals'][1:], marker='s', label='hour')

    plt.legend()

    pylab.savefig(savestring + 'averaging.png', bbox_inches='tight')



    print('end')

