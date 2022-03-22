import matplotlib.pyplot as plt
import numpy as np


def plot_difference(mod_142, obs_142, time_142,
                    mod_111, obs_111, time_111,
                    savepath):
    """
    Plot the differences between modeled variable and observation variable
    :param mod:
    :param obs:
    :param variable:
    :param time:
    :return:
    """

    plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)

    plt.plot([t.hour for t in time_142], (mod_142 - obs_142)/np.abs(obs_142), marker='o', label='123')
    plt.plot([t.hour for t in time_111], (mod_111 - obs_111)/np.abs(obs_111), marker='o', label='126')

    # plt.plot([t.hour for t in time_142], (obs_142 - mod_142)/np.abs(mod_142), marker='o', label='142')
    # plt.plot([t.hour for t in time_111], (obs_111 - mod_111)/np.abs(mod_111), marker='o', label='111')

    # plt.gcf().autofmt_xdate()
    # ax.xaxis.set_major_formatter(DateFormatter('%H'))

    plt.ylabel('($Q_{H}^{mod}$ - $Q_{H}^{obs}$) / $Q_{H}^{obs}$')
    plt.xlabel('Time (h)')

    plt.axhline(y=0, color='k', linestyle='-', linewidth=0.8)

    plt.legend()

    plt.savefig(savepath + 'test.png', bbox_inches='tight')

    print('end')

