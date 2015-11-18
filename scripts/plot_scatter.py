#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np

import plottingscripts.utils.plot_util as plot_util
import plottingscripts.plotting.scatter as scatter


def main():
    prog = "python plot_scatter.py"
    description = "Plots performances of the best config at one time vs another in a scatter plot"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    # parser.add_argument("-l", "--log", action="store_true", dest="log",
    #                     default=False, help="Plot on log scale")
    parser.add_argument("--max", dest="max", type=float,
                        default=1000, help="Maximum of both axes")
    parser.add_argument("--min", dest="min", type=float,
                        default=None, help="Minimum of both axes")
    parser.add_argument("-s", "--save", dest="save",
                        default="", help="Where to save plot instead of showing it?")
    parser.add_argument("--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--greyFactor", dest="grey_factor", type=float,
                        default=1, help="If an algorithms is not greyFactor-times better"
                                        " than the other, show this point less salient, > 1")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
                        help="Plot some debug info")
    parser.add_argument("-f", "--lineFactors", dest="linefactors",
                        default=None, help="Plot X speedup/slowdown, format 'X,..,X' (no spaces)")
    parser.add_argument("--time", dest="time", default=None,
                        help="Plot config at which time?, format 'time1,time2' ")
    parser.add_argument("--obj", dest="obj", default=None, required=True,
                        help="Path to validationObjectiveMatrix-traj-run-* file")
    parser.add_argument("--res", dest="res", required=True,
                        help="Path to validationResults-traj-run-* file")
    parser.add_argument("--minvalue", dest="minvalue", type=float,
                        help="Replace all values smaller than this",)
    parser.add_argument("--fontsize", dest="fontsize", type=int, default=20,
                        help="Use this fontsize for plotting",)

    args, unknown = parser.parse_known_args()

    if len(unknown) != 0:
        print "Wrong number of arguments"
        parser.print_help()
        sys.exit(1)

    if args.grey_factor < 1:
        print "A grey-factor lower than one makes no sense"
        parser.print_help()
        sys.exit(1)

    # Load validationResults
    res_header, res_data = plot_util.read_csv(args.res, has_header=True)
    av_times = [float(row[0]) for row in res_data]
    if args.time == None:
        # Print available times and quit
        print "Choose a time from"
        print "\n".join(["* %s" % i for i in av_times])
        sys.exit(0)
    time_arr = args.time.split(",")
    if len(time_arr) != 2 or (len(time_arr) == 2 and (time_arr[1] == "" or time_arr[0] == "")):
        print "Something wrong with %s, should be 'a,b'" % args.time
        print "Choose a time from"
        print "\n".join(["* %s" % i for i in av_times])
        sys.exit(0)
    time_1 = float(time_arr[0])
    time_2 = float(time_arr[1])

    # Now extract data
    config_1 = [int(float(row[len(res_header)-2].strip('"'))) for row in res_data if int(float(row[0])) == int(time_1)]
    config_2 = [int(float(row[len(res_header)-2].strip('"'))) for row in res_data if int(float(row[0])) == int(time_2)]
    if len(config_1) == 0 or len(config_2) == 0:
        print "Time int(%s) or int(%s) not found. Choose a time from:" % (time_1, time_2)
        print "\n".join(["* %s" % i for i in av_times])
        sys.exit(1)
    config_1 = config_1[0]
    config_2 = config_2[0]

    obj_header, obj_data = plot_util.read_csv(args.obj, has_header=True)
    head_template = '"Objective of validation config #%s"'
    idx_1 = obj_header.index(head_template % config_1)
    idx_2 = obj_header.index(head_template % config_2)

    data_one = np.array([float(row[idx_1].strip('"')) for row in obj_data])
    data_two = np.array([float(row[idx_2].strip('"')) for row in obj_data])

    print "Found %s points for config %d and %s points for config %d" % (str(data_one.shape), config_1, str(data_two.shape), config_2)

    linefactors = list()
    if args.linefactors is not None:
        linefactors = [float(i) for i in args.linefactors.split(",")]
        if len(linefactors) < 1:
            print "Something is wrong with linefactors: %s" % args.linefactors
            sys.exit(1)
        if min(linefactors) < 1:
            print "A line-factor lower than one makes no sense"
            sys.exit(1)
    if args.grey_factor > 1 and args.grey_factor not in linefactors:
        linefactors.append(args.grey_factor)

    label_template = 'Objective of validation config #%s, best at %s sec'
    
    # This might produce overhead for large .csv files
    times = [int(float(row[0])) for row in res_data]
    time_1 = res_data[times.index(int(time_1))][0]
    time_2 = res_data[times.index(int(time_2))][0]

    data_one = np.array([max(args.minvalue, i) for i in data_one])
    data_two = np.array([max(args.minvalue, i) for i in data_two])

    fig = scatter.plot_scatter_plot(x_data=data_one, y_data=data_two,
                                    labels=[label_template % (config_1, str(time_1)),
                                            label_template % (config_2, str(time_2))],
                                    title=args.title,
                                    max_val=args.max, min_val=args.min,
                                    grey_factor=args.grey_factor,
                                    linefactors=linefactors,
                                    user_fontsize=args.fontsize,
                                    debug=args.verbose)
    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()


if __name__ == "__main__":
    main()
