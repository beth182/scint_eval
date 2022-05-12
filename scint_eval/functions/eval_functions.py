import matplotlib.pyplot as plt
import numpy as np


def plot_difference(return_dict_123,
                    return_dict_126,
                    savepath):
    """
    Plot the differences between modeled variable and observation variable
    :param mod:
    :param obs:
    :param variable:
    :param time:
    :return:
    """

    mod_123_10, obs_123_10, time_123_10 = return_dict_123['mod_vals_eval_10'], return_dict_123['obs_vals_eval_10'], return_dict_123['time_eval_10']
    mod_126_10, obs_126_10, time_126_10 = return_dict_126['mod_vals_eval_10'], return_dict_126['obs_vals_eval_10'], return_dict_126['time_eval_10']

    mod_123_1, obs_123_1, time_123_1 = return_dict_123['mod_vals_eval_1'], return_dict_123['obs_vals_eval_1'], return_dict_123['time_eval_1']
    mod_126_1, obs_126_1, time_126_1 = return_dict_126['mod_vals_eval_1'], return_dict_126['obs_vals_eval_1'], return_dict_126['time_eval_1']

    mod_123_5, obs_123_5, time_123_5 = return_dict_123['mod_vals_eval_5'], return_dict_123['obs_vals_eval_5'], return_dict_123['time_eval_5']
    mod_126_5, obs_126_5, time_126_5 = return_dict_126['mod_vals_eval_5'], return_dict_126['obs_vals_eval_5'], return_dict_126['time_eval_5']

    mod_123_60, obs_123_60, time_123_60 = return_dict_123['mod_vals_eval_60'], return_dict_123['obs_vals_eval_60'], return_dict_123['time_eval_60']
    mod_126_60, obs_126_60, time_126_60 = return_dict_126['mod_vals_eval_60'], return_dict_126['obs_vals_eval_60'], return_dict_126['time_eval_60']

    diff_1_123 = (mod_123_1 - obs_123_1) / np.abs(obs_123_1)
    diff_1_126 = (mod_126_1 - obs_126_1) / np.abs(obs_126_1)

    diff_10_123 = (mod_123_10 - obs_123_10) / np.abs(obs_123_10)
    diff_10_126 = (mod_126_10 - obs_126_10) / np.abs(obs_126_10)

    diff_5_123 = (mod_123_5 - obs_123_5) / np.abs(obs_123_5)
    diff_5_126 = (mod_126_5 - obs_126_5) / np.abs(obs_126_5)

    diff_60_123 = (mod_123_60 - obs_123_60) / np.abs(obs_123_60)
    diff_60_123 = diff_60_123[:-1]
    diff_60_126 = (mod_126_60 - obs_126_60) / np.abs(obs_126_60)

    av_diff_1_123 = np.average(np.abs(diff_1_123))
    av_diff_5_123 = np.average(np.abs(diff_5_123))
    av_diff_10_123 = np.average(np.abs(diff_10_123))
    av_diff_60_123 = np.average(np.abs(diff_60_123))

    av_diff_1_126 = np.average(np.abs(diff_1_126))
    av_diff_5_126 = np.average(np.abs(diff_5_126))
    av_diff_10_126 = np.average(np.abs(diff_10_126))
    av_diff_60_126 = np.average(np.abs(diff_60_126))

    print(av_diff_1_123)
    print(av_diff_5_123)
    print(av_diff_10_123)
    print(av_diff_60_123)
    print(' ')

    print(av_diff_1_126)
    print(av_diff_5_126)
    print(av_diff_10_126)
    print(av_diff_60_126)


    plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)

    plt.plot([t.hour for t in time_123_1], diff_1_123, marker='x', label='Cloudy 1', color='black', linestyle='dotted')
    plt.plot([t.hour for t in time_126_1], diff_1_126, marker='o', label='Clear 1', color='black')

    plt.plot([t.hour for t in time_123_10], diff_10_123, marker='x', label='Cloudy 10', color='red', linestyle='dotted')
    plt.plot([t.hour for t in time_126_10], diff_10_126, marker='o', label='Clear 10', color='red')

    plt.plot([t.hour for t in time_123_5], diff_5_123, marker='x', label='Cloudy 5', color='green', linestyle='dotted')
    plt.plot([t.hour for t in time_126_5], diff_5_126, marker='o', label='Clear 5', color='green')

    plt.plot([t.hour for t in time_123_60][:-1], diff_60_123, marker='x', label='Cloudy 60', color='purple', linestyle='dotted')
    plt.plot([t.hour for t in time_126_60], diff_60_126, marker='o', label='Clear 60', color='purple')


    # plt.gcf().autofmt_xdate()
    # ax.xaxis.set_major_formatter(DateFormatter('%H'))

    plt.ylabel('($Q_{H}^{mod}$ - $Q_{H}^{obs}$) / $Q_{H}^{obs}$')
    plt.xlabel('Time (h)')

    plt.axhline(y=0, color='k', linestyle='-', linewidth=0.8)

    plt.legend(fontsize=15)

    plt.savefig(savepath + 'test.png', bbox_inches='tight')

    print('end')

