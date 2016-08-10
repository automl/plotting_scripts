#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np

from plottingscripts.utils import read_util, plot_util
import plottingscripts.plotting.plot_methods as plot_methods


def main():
    prog = "python plot_performance_wo_Timeouts <WhatIsThis> " \
           "one/or/many/validationObjectiveMatrix*.csv"
    description = "Plot a median trace with quantiles for multiple " \
                  "experiments, but ignore Timeouts"

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
    parser.add_argument("--ylabel", dest="ylabel", default=None,
                        help="Label on y-axis")
    parser.add_argument("-s", "--save", dest="save",
                        default="",
                        help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="",
                        help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint,
                        help="Replace all values higher than this?")
    parser.add_argument("--agglomeration", dest="agglomeration", type=str,
                        default="median", choices=("median", "mean"),
                        help="Plot mean or median")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")
    parser.add_argument("-c", "--cutoff", dest="cutoff", required=True,
                        type=float, help="Cutoff of this scenario")

    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    if args.ylabel is None:
        args.ylabel = "%s performance on instances" % args.agglomeration

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv')
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for
                     i in range(len(name_list))]

    # Get data from csv
    performance = list()
    time_ = list()

    for name in range(len(name_list)):
        # We have a new experiment
        performance.append(list())
        time_.append([1, 2])
        for fl in file_list[name]:
            data_dict = read_util.read_validationObjectiveMatrix_file(fl)
            # Get Performance for each step
            tmp_performance = list()
            for idx in [0, -1]:
                summer = [data_dict[inst][idx] for inst in data_dict.keys()]
                summer = np.array(summer)
                notTimeout_idx = summer < args.cutoff
                summer = summer[notTimeout_idx]
                tmp_performance.append(np.mean(summer))
            performance[-1].append(tmp_performance)

    performance = [np.array(i) for i in performance]

    # This plotting function requires a time array for each experiment
    fig = plot_methods.plot_optimization_trace_mult_exp(time_list=time_,
                                                        performance_list=performance,
                                                        title=args.title,
                                                        name_list=name_list,
                                                        logx=args.logx,
                                                        logy=args.logy,
                                                        y_max=args.ymax,
                                                        y_min=args.ymin,
                                                        x_min=0.8,
                                                        x_max=2.2,
                                                        agglomeration=args.agglomeration,
                                                        ylabel=args.ylabel)

    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()

if __name__ == "__main__":
    main()