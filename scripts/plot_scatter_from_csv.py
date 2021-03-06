#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np

from plottingscripts.utils import read_util, plot_util
import plottingscripts.plotting.scatter as scatter


def main():
    prog = "python plot_scatter.py any.csv"
    description = "Reads performances from a two-column .csv and creates a" \
                  " scatterplot"

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
                        default=None, help="Plot X speedup/slowdown, format "
                                           "'X,..,X' (no spaces)")
    parser.add_argument("-c", "--columns", dest="columns", default='1,2',
                        help="Use these columns from csv; starting at 1, format"
                             " 'xaxis,yaxis' (nospaces)")
    parser.add_argument("--size", dest="user_fontsize", default=12, type=int,
                        help="Standard fontsize")
    parser.add_argument("--dpi", dest="dpi", default=100, type=int,
                        help="DPI for saved figure")

    args, unknown = parser.parse_known_args()

    if len(unknown) != 1:
        print "Wrong number of arguments"
        parser.print_help()
        sys.exit(1)

    if args.grey_factor < 1:
        print "A grey-factor lower than one makes no sense"
        parser.print_help()
        sys.exit(1)

    # Check selected columns
    columns = [int(float(i)) for i in args.columns.split(",")]
    if len(columns) != 2:
        raise ValueError("Selected more or less than two columns: %s" %
                         str(columns))
    # As python starts with 0
    columns = [i-1 for i in columns]

    # Load validationResults
    res_header, res_data = read_util.read_csv(unknown[0], has_header=True,
                                              data_type=np.float)
    res_data = np.array(res_data)
    print "Found %s points" % (str(res_data.shape))

    # Get data
    if max(columns) > res_data.shape[1]-1:
        raise ValueError("You selected column %d, but there are only %d" %
                         (max(columns)+1, res_data.shape[1]))
    if min(columns) < 0:
        raise ValueError("You selected a column number less than 1")
    data_x = res_data[:, columns[0]]
    data_y = res_data[:, columns[1]]
    label_x = res_header[columns[0]]
    label_y = res_header[columns[1]]

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

    fig = scatter.plot_scatter_plot(x_data=data_x, y_data=data_y,
                                    labels=[label_x, label_y],
                                    title=args.title,
                                    max_val=args.max,
                                    min_val=args.min,
                                    grey_factor=args.grey_factor,
                                    linefactors=linefactors,
                                    debug=args.verbose,
                                    user_fontsize=args.user_fontsize,
                                    dpi=args.dpi)

    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()

if __name__ == "__main__":
    main()
