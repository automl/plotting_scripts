#!/usr/bin/env python

from argparse import ArgumentParser
import csv
import sys

import numpy as np

import load_data


def fill_trajectory(performance_list, time_list):
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
        del t_list

        # Append time to the list for this exp
        exp_time.append(time_list[low_idx][time_idx[low_idx]])

        # Check whether there is any other exp with the same timestep
        low_time = time_list[low_idx][time_idx[low_idx]]
        for idx in range(num_exp):
            if time_list[idx][time_idx[idx]] == low_time:
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
    return performance, time_

def main():
    prog = "python merge_performance_different_times.py <WhatIsThis> " \
           "one/or/many/*ClassicValidationResults*.csv"
    description = "Merge results to one csv"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint,
                        help="Replace all values higher than this?")
    parser.add_argument("--save", dest="saveTo", type=str,
                        required=True, help="Where to save the csv?")

    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 1:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    # Get files and names
    arg_list = list(["dummy", ])
    arg_list.extend(unknown)
    file_list, name_list = load_data.get_file_and_name_list(arg_list, match_file='.csv')
    del arg_list

    for time_idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[time_idx], len(file_list[time_idx]))
    if len(file_list) > 1:
        sys.stderr.write("Cannot handle more than one experiment")
        parser.print_help()
        sys.exit(1)

    file_list = file_list[0]

    # Get data from csv
    performance_list = list()
    time_list = list()

    for fl in file_list:
        _none, csv_data = load_data.read_csv(fl, has_header=True)
        csv_data = np.array(csv_data)
        # Replace too high values with args.maxint
        testdata = [min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 2]]
        #traindata = [min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 1]]
        time_steps = [float(i.strip()) for i in csv_data[:, 0]]
        # assert time_steps[0] == 0
        if time_steps[0] != 0:
            time_steps.insert(0, 0)
            testdata = [1-i for i in testdata]
            testdata.insert(0, 2)
            
        performance_list.append(testdata)
        time_list.append(time_steps)

    performance, time_ = fill_trajectory(performance_list=performance_list, time_list=time_list)

    fh = open(args.saveTo, 'w')
    writer = csv.writer(fh)
    header = ["Time", ]
    header.extend([fl for fl in file_list])
    writer.writerow(header)
    for r, t in enumerate(time_):
        row = list([t, ])
        row.extend([p[r] for p in performance])
        writer.writerow(row)
    fh.close()


if __name__ == "__main__":
    main()
