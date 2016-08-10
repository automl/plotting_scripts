import csv
import sys

import numpy as np
import pandas as pd

import plottingscripts.utils.read_util as plot_util


def fill_trajectory(performance_list, time_list, replace_nan=np.NaN):
    frame_dict = dict()
    counter = np.arange(0, len(performance_list))
    for p, t, c in zip(performance_list, time_list, counter):
        if len(p) != len(t):
            raise ValueError("(%d) Array length mismatch: %d != %d" %
                             (c, len(p), len(t)))
        frame_dict[str(c)] = pd.Series(data=p, index=t)

    merged = pd.DataFrame(frame_dict)
    merged = merged.ffill()

    print(merged.get_values())

    performance = merged.get_values()
    time_ = merged.index.values

    performance[np.isnan(performance)] = replace_nan

    if not np.isfinite(performance).all():
        raise ValueError("\nCould not merge lists, because \n"
                         "\t(a) one list is empty?\n"
                         "\t(b) the lists do not start with the same times and"
                         " replace_nan is not set?\n"
                         "\t(c) any other reason.")



    """ Replace the following with PandaFrames
    # Fill times
    len_exp = list([len(i) for i in performance_list])
    num_exp = len(performance_list)

    time_idx = list([1 for i in range(num_exp)])
    perf_idx = list([0 for i in range(num_exp)])
    exp_time = list([0, ])
    perf_list = [list([performance_list[i][0], ]) for i in range(num_exp)]

    while True:
        # Find out exp with lowest time
        t_list = [sys.maxint if time_idx[i] == -1 else time_list[i][time_idx[i]] for i in range(num_exp)]
        low_idx = np.argmin(t_list)
        if t_list[low_idx] == sys.maxint:
            break
        del t_list, i

        low_time = time_list[low_idx][time_idx[low_idx]]
        # Append time to the list for this exp
        exp_time.append(low_time)
        if exp_time[-1] < exp_time[-1]:
            raise ValueError()

        # Check whether there is any other exp with the same timestep
        for idx in range(num_exp):
            # Sanity check
            if time_list[idx][time_idx[idx]] < low_time and time_idx[idx] != -1:
                raise ValueError("Something terribly wrong")

            if time_list[idx][time_idx[idx]] == low_time and time_idx[idx] != -1:
                time_idx[idx] += 1
                perf_idx[idx] += 1
        del low_time

        # Append performance
        for i in range(num_exp):
            perf_list[i].append(performance_list[i][perf_idx[i]])

        # Check whether we are at the end for any exp
        time_idx = [time_idx[t] if time_idx[t] < len_exp[t] else -1 for t in range(num_exp)]
        perf_idx = [perf_idx[t] if perf_idx[t] < len_exp[t] else -1 for t in range(num_exp)]
    # We don't need this anymore
    del time_idx
    del perf_idx

    # Now clean data as sometimes the incumbent doesn't change over time
    last_perf = [i*10 for i in range(num_exp)]  # dummy entry
    time_ = list()
    performance = list([list() for i in range(num_exp)])
    for idx, t in enumerate(exp_time):
        # print t, idx, last_perf, perf_list[0][idx], perf_list[1][idx]
        diff = sum([np.abs(last_perf[i] - perf_list[i][idx]) for i in range(num_exp)])
        if diff != 0 or idx == 0 or idx == len(exp_time) - 1:
            # always use first and last entry
            time_.append(t)
            [performance[i].append(perf_list[i][idx]) for i in range(num_exp)]
        last_perf = [p[idx] for p in perf_list]

    print "len(performance)", [len(p) for p in performance]
    # print "Performance", performance
    print "len(time)", len(time_)
    # print "Time steps", time_
    """
    return performance, time_