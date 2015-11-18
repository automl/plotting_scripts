#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np

import plottingscripts.utils.plot_util as plot_util
import plottingscripts.plotting.plot_methods as plot_methods
import plottingscripts.utils.merge_test_performance_different_times as merge_test_performance_different_times


def main():
    prog = "python plot_performance <WhatIsThis> one/or/many/runs_and_results*.csv"
    description = "Plot a median trace with quantiles for multiple experiments"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    parser.add_argument("-l", "--log", action="store_true", dest="log",
                        default=False, help="Plot on log scale")
    parser.add_argument("--ymax", dest="ymax", type=float,
                        default=None, help="Maximum of the y-axis")
    parser.add_argument("--ymin", dest="ymin", type=float,
                        default=None, help="Minimum of the y-axis")
    parser.add_argument("--xmax", dest="xmax", type=float,
                        default=None, help="Maximum of the x-axis")
    parser.add_argument("--xmin", dest="xmin", type=float,
                        default=None, help="Minimum of the x-axis")
    parser.add_argument("-s", "--save", dest="save", default="",
                        help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title", default="",
                        help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint,
                        help="Replace all values higher than this?")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")
    parser.add_argument("--agglomeration", dest="agglomeration", type=str,
                        default="mean", help="Show mean or median",
                        choices=("mean", "median"))

    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    # Get files and names
    file_list, name_list = plot_util.get_file_and_name_list(unknown, match_file=".")
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i in range(len(name_list))]

    # Get data from csv
    performance_list = list()
    time_list = list()

    show_from = -sys.maxint

    for name in range(len(name_list)):
        # We have a new experiment
        performance = list()
        time_ = list()
        for fl in file_list[name]:
            _none, csv_data = plot_util.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)

            # Replace too high values with args.maxint
            data = [min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 1]]

            # do we have only non maxint data?
            show_from = max(data.count(args.maxvalue), show_from)

            performance.append(data)
            time_.append([float(i.strip()) for i in csv_data[:, 2]])
        if len(time_) > 1:
            print len(time_)
            performance, time_ = merge_test_performance_different_times.fill_trajectory(performance_list=performance, time_list=time_)
            print performance[0][:10]
        else:
            time_ = time_[0]
        performance = [np.array(i) for i in performance]
        time_ = np.array(time_)
        performance_list.append(performance)
        time_list.append(time_)

    if args.xmin is None and show_from != 0:
        args.xmin = show_from

    print time_list[0].shape
    print performance_list[0][0].shape

    fig = plot_methods.plot_optimization_trace_mult_exp(time_list=time_list,
                                                        performance_list=performance_list,
                                                        title=args.title,
                                                        name_list=name_list,
                                                        logx=args.log, logy=False,
                                                        agglomeration=args.agglomeration,
                                                        y_min=args.ymin,
                                                        y_max=args.ymax,
                                                        x_min=args.xmin,
                                                        x_max=args.xmax)

    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()

if __name__ == "__main__":
    main()
