#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np

from plottingscripts.utils import read_util, plot_util
import plottingscripts.plotting.plot_methods as plot_methods


def main():
    prog = "python plot_ac_overhead <WhatIsThis> one/or/many/*ValidationResults-traj-run*.csv"
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
                        default="", help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint, help="Replace all values higher than this?")
    parser.add_argument("--agglomeration", dest="agglomeration", type=str,
                        default="median", choices=("median", "mean"),
                        help="Plot mean or median")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
                        help="print number of runs on plot")
    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    if args.ylabel is None:
        args.ylabel = "%s AC overhead [sec]" % args.agglomeration

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown, match_file='.csv')
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i in range(len(name_list))]

    # Get data from csv
    overhead = list()
    time_ = list()
    show_from = -sys.maxint

    for name in range(len(name_list)):
        # We have a new experiment
        overhead.append(list())
        for fl in file_list[name]:
            _none, csv_data = read_util.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)
            overhead[-1].append(csv_data[:, 3])
            time_.append([float(i.strip()) for i in csv_data[:, 0]])
            # Check whether we have the same times for all runs
            if len(time_) == 2:
                if time_[0] == time_[1]:
                    time_ = [time_[0], ]
                else:
                    raise NotImplementedError(".csv are not using the same times")
    overhead = [np.array(i, dtype=np.float32) for i in overhead]
    # print time_
    time_ = np.array(time_).flatten()

    # This plotting function requires a time array for each experiment
    new_time_list = [time_ for i in range(len(overhead))]
    fig = plot_methods.plot_optimization_trace_mult_exp(time_list=new_time_list,
                                                        performance_list=overhead,
                                                        title=args.title,
                                                        name_list=name_list,
                                                        logx=args.logx,
                                                        logy=args.logy,
                                                        y_min=args.ymin,
                                                        y_max=args.ymax,
                                                        x_min=args.xmin,
                                                        x_max=args.xmax,
                                                        agglomeration=args.agglomeration,
                                                        ylabel=args.ylabel)

    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()

if __name__ == "__main__":
    main()