#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import csv
import itertools
import sys

import plot_util
import plot_methods


def main():
    prog = "python merge_performance_different_times.py <WhatIsThis> " \
           "one/or/many/*ClassicValidationResults*.csv"
    description = "Merge results to one csv"

    parser = ArgumentParser(description=description, prog=prog,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # General Options
    parser.add_argument("--logy", action="store_true", dest="logy",
                        default=False, help="Plot y-axis on log scale")
    parser.add_argument("--logx", action="store_true", dest="logx",
                        default=False, help="Plot x-axis on log scale")
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
                        default=None, help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint, help="Replace all values higher than this?")
    parser.add_argument("--ylabel", dest="ylabel",
                        default="Minfunction value", help="y label")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
                        help="print number of runs on plot")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))
    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    # Get files and names
    file_list, name_list = plot_util.get_file_and_name_list(unknown, match_file='.csv')
    for idx in range(len(name_list)):
        assert len(file_list[idx]) == 1, "%s" % str(file_list[idx])
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    times = list()
    performances = list()
    for idx, name in enumerate(name_list):
        t = None
        p = None
        print "Processing %s" % name
        fh = open(file_list[idx][0], 'r')
        reader = csv.reader(fh)
        for row in reader:
            if t is None:
                # first row
                p = list([list() for i in range(len(row)-1)])
                t = list()
                continue
            t.append(float(row[0]))
            del row[0]
            [p[i].append(float(row[i])) for i in range(len(row))]
        times.append(t)
        performances.append(p)

    # Sort names alphabetical as done here:
    # http://stackoverflow.com/questions/15610724/sorting-multiple-lists-in-python-based-on-sorting-of-a-single-list
    sorted_lists = sorted(itertools.izip(name_list, times, performances), key=lambda x: x[0])
    name_list, times, performances = [[x[i] for x in sorted_lists] for i in range(3)]

    prop = {}
    args_dict = vars(args)
    for key in defaults:
        prop[key] = args_dict[key]

    plot_methods.plot_optimization_trace_mult_exp(time_list=times,
                                                  performance_list=performances,
                                                  title=args.title,
                                                  name_list=name_list,
                                                  ylabel=args.ylabel,
                                                  logy=args.logy,
                                                  logx=args.logx,
                                                  save=args.save,
                                                  y_min=args.ymin,
                                                  y_max=args.ymax,
                                                  x_min=args.xmin,
                                                  x_max=args.xmax,
                                                  properties=prop, scale_std=1)


if __name__ == "__main__":
    main()