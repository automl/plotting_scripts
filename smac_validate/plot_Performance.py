#!/usr/bin/env python

from argparse import ArgumentParser
import os
import sys
import itertools

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show
import matplotlib.gridspec
import numpy as np

import load_data


def plot_optimization_trace(times, performance_list, title, name_list, log=False, save="",
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

    for idx, performance in enumerate(performance_list):
        color = colors.next()
        # Get mean and std
        if log:
            performance = np.log10(performance)

        median = np.median(performance, axis=0)
        upper_quartile = np.percentile(performance, q=75, axis=0)
        lower_quartile = np.percentile(performance, q=25, axis=0)
        # Plot mean and std
        ax1.fill_between(times, lower_quartile, upper_quartile,
                         facecolor=color, alpha=0.3, edgecolor=color)
        ax1.plot(times, median, color=color, linewidth=size,
                 linestyle=linestyles, marker=markers, label=name_list[idx])

        # Get limits
        # For y_min we always take the lowest value
        auto_y_min = min(min(lower_quartile[x_min:]), auto_y_min)

        # For y_max we take the highest value after the median/quartile starts to change
        init_per = median[0]
        init_up = upper_quartile[0]
        init_lo = lower_quartile[0]
        init_idx = 0
        # Find out when median/quartile changes
        while init_idx < len(median) and init_per == median[init_idx] and \
                init_up == upper_quartile[init_idx] and \
                init_lo == lower_quartile[init_idx]:
            # stop when median/quartile changes
            init_idx += 1

        # Found the first change, but show two more points on the left side
        init_idx = max(0, init_idx-3)
        if init_idx >= 0:
            # median stays the same for > 1 evaluations
            auto_x_min = min(times[init_idx], auto_x_min)

        from_ = max(init_idx, x_min)
        auto_y_max = max(max(upper_quartile[from_:]), auto_y_max)
    auto_x_max = times[-1]

    # Describe axes
    if log:
        ax1.set_ylabel("log10(Performance)")
    else:
        ax1.set_ylabel("Performance")
    ax1.set_xlabel("log10(time) [sec]")

    leg = ax1.legend(loc='best', fancybox=True)
    leg.get_frame().set_alpha(0.5)

    # Set axes limits
    ax1.set_xscale("log")
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
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min), auto_x_max + 0.1*abs(auto_x_max)])

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
        print(parser.usage)
        sys.exit(1)

    # Get files and names
    file_list, name_list = load_data.get_file_and_name_list(unknown, match_file='.csv')
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
            _none, csv_data = load_data.read_csv(fl, has_header=True)
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
    plot_optimization_trace(times=time_, performance_list=performance, title=args.title,
                            name_list=name_list, log=args.log, save=save, y_min=args.ymin,
                            y_max=args.ymax, x_min=args.xmin, x_max=args.xmax)

if __name__ == "__main__":
    main()