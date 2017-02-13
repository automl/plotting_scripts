#!/usr/bin/env python

from argparse import ArgumentParser
import itertools
import os
import sys

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from plottingscripts.utils import read_util, plot_util, helper
import plottingscripts.plotting.plot_methods as plot_methods
import plottingscripts.utils.macros
import plottingscripts.utils.merge_test_performance_different_times as \
    merge_test_performance_different_times


def main():
    prog = "python plot_TestvsTrainPerformance.py <WhatIsThis> " \
           "one/or/many/*ClassicValidationResults*.csv"
    description = "Plot a median trace with quantiles for multiple experiments"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    parser.add_argument("--logx", action="store_true", dest="logx",
                        default=False, help="Plot x-axis on log scale")
    parser.add_argument("--logy", action="store_true", dest="logy",
                        default=False, help="Plot y-axis on log scale")
    parser.add_argument("--ymax", dest="ymax", type=float,
                        default=None, help="Maximum of the y-axis")
    parser.add_argument("--ymin", dest="ymin", type=float,
                        default=None, help="Minimum of the y-axis")
    parser.add_argument("--xmax", dest="xmax", type=float,
                        default=None, help="Maximum of the x-axis")
    parser.add_argument("--xmin", dest="xmin", type=float,
                        default=None, help="Minimum of the x-axis")
    parser.add_argument("--ylabel", dest="ylabel", default=None,
                        help="Label on y-axis")
    parser.add_argument("-s", "--save", dest="save",
                        default="",
                        help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=plottingscripts.utils.macros.MAXINT,
                        help="Replace all values higher than this?")
    parser.add_argument("--agglomeration", dest="agglomeration", type=str,
                        default="median", choices=("median", "mean"),
                        help="Plot mean or median")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))
    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print("To less arguments given")
        parser.print_help()
        sys.exit(1)

    if args.ylabel is None:
        args.ylabel = "%s performance on instances" % args.agglomeration

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv')
    for idx in range(len(name_list)):
        print("%20s contains %d file(s)" %
              (name_list[idx], len(file_list[idx])))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")"
                     for i in range(len(name_list))]

    name_list_test_train, new_time_list, performance = get_performance_data(
        file_list, name_list, args.maxvalue)

    properties = helper.fill_property_dict(arguments=args, defaults=defaults)

    if len(name_list) > 1:
        properties["linestyles"] = itertools.cycle([":", "-"])
        c = []
        cycle = plot_util.get_defaults()["colors"]
        for i in range(10):
            color = next(cycle)
            c.extend([color, color])
        properties["colors"] = itertools.cycle(c)
        properties["markers"] = itertools.cycle([""])

    fig = plot_methods.\
        plot_optimization_trace_mult_exp(time_list=new_time_list,
                                         performance_list=performance,
                                         title=args.title,
                                         name_list=name_list_test_train,
                                         logx=args.logx, logy=args.logy,
                                         y_min=args.ymin,
                                         y_max=args.ymax,
                                         x_min=args.xmin,
                                         x_max=args.xmax,
                                         agglomeration=args.agglomeration,
                                         ylabel=args.ylabel,
                                         properties=properties)

    if args.save != "":
        print("Save plot to %s" % args.save)
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()


def get_performance_data(file_list, name_list, maxvalue):
    # Get data from csv
    performance = list()
    time_ = list()
    name_list_test_train = []
    for name in range(len(name_list)):
        # We have a new experiment
        trn_perf = []
        tst_perf = []
        time_for_name = []

        for fl in file_list[name]:
            _none, csv_data = read_util.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)
            # Replace too high values with args.maxint
            train_data = [min([maxvalue, float(i.strip())])
                          for i in csv_data[:, 1]]
            test_data = [min([maxvalue, float(i.strip())])
                         for i in csv_data[:, 2]]
            time_data = [float(i.strip()) for i in csv_data[:, 0]]

            trn_perf.append(train_data)
            tst_perf.append(test_data)
            time_for_name.append(time_data)

        merged_performances = trn_perf + tst_perf
        len_trn_perf = len(trn_perf)
        merged_time = time_for_name + time_for_name

        merged_performances, merged_time = merge_test_performance_different_times. \
            fill_trajectory(merged_performances, merged_time)
        trn_perf = merged_performances[:, :len_trn_perf]
        tst_perf = merged_performances[:, len_trn_perf:]

        # Convert to numpy arrays
        trn_perf = np.array(trn_perf)
        tst_perf = np.array(tst_perf)
        merged_time = np.array(merged_time)

        # Append performance to global plotting array
        name_list_test_train.append("%s_train" % name_list[name])
        performance.append(trn_perf.transpose())
        name_list_test_train.append("%s_test" % name_list[name])
        performance.append(tst_perf.transpose())
        # Append the time twice, once for the test, once for the training array
        time_.append(merged_time)
        time_.append(merged_time)
    performance = np.array([np.array(i) for i in performance])
    time_ = np.array(time_)
    # This plotting function requires a time array for each experiment
    # new_time_list = np.array([time_ for i in range(len(performance))])
    new_time_list = np.array(time_)
    return name_list_test_train, new_time_list, performance


if __name__ == "__main__":
    main()
