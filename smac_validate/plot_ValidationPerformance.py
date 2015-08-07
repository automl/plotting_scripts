#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np

import plot_util
import plot_methods


def main():
    prog = "python plot_performance <WhatIsThis> one/or/many/*ClassicValidationResults*.csv"
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
    parser.add_argument("-s", "--save", dest="save",
                        default="", help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint, help="Replace all values higher than this?")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
                        help="print number of runs on plot")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--train', dest="train",  default=False, action='store_true')
    group.add_argument('--test', dest="test", default=True, action='store_true')

    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    # Get files and names
    file_list, name_list = plot_util.get_file_and_name_list(unknown, match_file='.csv')
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i in range(len(name_list))]

    # Get data from csv
    performance = list()
    time_ = list()
    show_from = -sys.maxint

    for name in range(len(name_list)):
        # We have a new experiment
        performance.append(list())
        for fl in file_list[name]:
            _none, csv_data = plot_util.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)
            # Replace too high values with args.maxint
            if args.train:
                data = [min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 1]]
            elif args.test:
                data = [min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 2]]
            else:
                print "This should not happen"
            # do we have only non maxint data?
            show_from = max(data.count(args.maxvalue), show_from)
            performance[-1].append(data)
            time_.append([float(i.strip()) for i in csv_data[:, 0]])
            # Check whether we have the same times for all runs
            if len(time_) == 2:
                if time_[0] == time_[1]:
                    time_ = [time_[0], ]
                else:
                    raise NotImplementedError(".csv are not using the same times")
    performance = [np.array(i) for i in performance]
    # print time_
    time_ = np.array(time_).flatten()

    if args.train:
                print "Plot TRAIN performance"
    elif args.test:
                print "Plot TEST performance"
    else:
        print "Don't know what I'm printing"

    if args.xmin is None and show_from != 0:
        args.xmin = show_from

    save = ""
    if args.save != "":
        save = args.save
        print "Save to %s" % args.save
    else:
        print "Show"
    plot_methods.plot_optimization_trace(times=time_,
                                         performance_list=performance,
                                         title=args.title, name_list=name_list,
                                         log=args.log, save=save,
                                         y_min=args.ymin, y_max=args.ymax,
                                         x_min=args.xmin, x_max=args.xmax)

if __name__ == "__main__":
    main()