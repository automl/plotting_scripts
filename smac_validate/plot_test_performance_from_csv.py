#!/usr/bin/env python

from argparse import ArgumentParser
import csv
import itertools
import sys

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show
import matplotlib.gridspec
import numpy as np

import load_data


def plot_optimization_trace(time_list, performance_list, title, name_list,
                            logy=False, logx=False, save="",
                            y_min=None, y_max=None, x_min=None, x_max=None):
    markers = 'o'
    colors = itertools.cycle(["#e41a1c",    # Red
                              "#377eb8",    # Blue
                              "#4daf4a",    # Green
                              "#984ea3",    # Purple
                              "#ff7f00",    # Orange
                              "#ffff33",    # Yellow
                              "#a65628",    # Brown
                              "#f781bf",    # Pink
                              "#999999"])   # Grey
    linestyles = '-'
    size = 1

    # Set up figure
    ratio = 5
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=100)
    fig.suptitle(title, fontsize=16)
    ax1 = subplot(gs[0:ratio, :])
    ax1.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

    auto_y_min = sys.maxint
    auto_y_max = -sys.maxint
    auto_x_min = sys.maxint
    auto_x_max = -sys.maxint

    for idx, performance in enumerate(performance_list):
        color = colors.next()
        if logy:
            performance = np.log10(performance)
        if logx and time_list[idx][0] == 0:
            time_list[idx][0] = 10**-5

        mean = np.mean(performance, axis=0)
        std = np.std(performance, axis=0)
        # Plot mean and std
        ax1.fill_between(time_list[idx], mean-std, mean+std,
                         facecolor=color, alpha=0.3, edgecolor=color)
        ax1.plot(time_list[idx], mean, color=color, linewidth=size,
                 linestyle=linestyles, marker=markers, label=name_list[idx])

        # Get limits
        # For y_min we always take the lowest value
        auto_y_min = min(min(mean-std[x_min:]), auto_y_min)
        auto_y_max = max(max(mean+std[x_min:]), auto_y_max)

        auto_x_min = min(time_list[idx][0], auto_x_min)
        auto_x_max = max(time_list[idx][-1], auto_x_max)

    # Describe axes
    if logy:
        ax1.set_ylabel("log10(Performance)")
    else:
        ax1.set_ylabel("Performance")

    if logx:
        ax1.set_xlabel("log10(time) [sec]")
        ax1.set_xscale("log")
        auto_x_min = max(0.1, auto_x_min)
    else:
        ax1.set_xlabel("time [sec]")

    leg = ax1.legend(loc='best', fancybox=True)
    leg.get_frame().set_alpha(0.5)

    # Set axes limits
    if y_max is None and y_min is not None:
        ax1.set_ylim([y_min, auto_y_max + 0.01*abs(auto_y_max - y_min)])
    elif y_max is not None and y_min is None:
        ax1.set_ylim([auto_y_min - 0.01*abs(auto_y_max - y_min), y_max])
    elif y_max > y_min and y_max is not None and y_min is not None:
        ax1.set_ylim([y_min, y_max])
    else:
        ax1.set_ylim([auto_y_min - 0.01*abs(auto_y_max - auto_y_min), auto_y_max + 0.01*abs(auto_y_max - auto_y_min)])

    if x_max is None and x_min is not None:
        ax1.set_xlim([x_min - 0.1*abs(x_min), auto_x_max + 0.1*abs(auto_x_max)])
    elif x_max is not None and x_min is None:
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min), x_max + 0.1*abs(x_max)])
    elif x_max > x_min and x_max is not None and x_min is not None:
        ax1.set_xlim([x_min, x_max])
    else:
        ax1.set_xlim([auto_x_min, auto_x_max + 0.1*abs(auto_x_min - auto_x_max)])

    # Save or show
    tight_layout()
    subplots_adjust(top=0.85)
    if save != "":
        savefig(save, dpi=100, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.1)
    else:
        show()


def main():
    prog = "python merge_performance_different_times.py <WhatIsThis> " \
           "one/or/many/*ClassicValidationResults*.csv"
    description = "Merge results to one csv"

    parser = ArgumentParser(description=description, prog=prog)

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
    file_list, name_list = load_data.get_file_and_name_list(unknown, match_file='.csv')
    for idx in range(len(name_list)):
        assert len(file_list[idx]) == 1
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

    save = ""
    if args.save != "":
        save = args.save
        print "Save to %s" % args.save
    else:
        print "Show"
    plot_optimization_trace(time_list=times, performance_list=performances, title=args.title,
                            name_list=name_list, logy=args.logy, logx=args.logx, save=save, y_min=args.ymin,
                            y_max=args.ymax, x_min=args.xmin, x_max=args.xmax)



if __name__ == "__main__":
    main()