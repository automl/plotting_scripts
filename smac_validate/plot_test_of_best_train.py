#!/usr/bin/env python

from argparse import ArgumentParser
import sys
import itertools

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show
import matplotlib.gridspec
import numpy as np

import load_data


def plot_optimization_trace(times, performance_list, title, min_test, max_test, name_list,
                            log=False, save="", y_min=None, y_max=None, x_min=None, x_max=None):
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

    # set initial limits
    auto_y_min = sys.maxint
    auto_y_max = -sys.maxint
    auto_x_min = sys.maxint

    for idx, performance in enumerate(performance_list):
        if log:
            performance = np.log10(performance)
            min_test[idx] = np.log10(min_test[idx])
            max_test[idx] = np.log10(max_test[idx])
        color = colors.next()
        # Plot stuff
        ax1.plot(times, performance, color=color, linewidth=size,
                 linestyle=linestyles, marker=markers, label=name_list[idx])
        ax1.fill_between(times, min_test[idx], max_test[idx], facecolor=color, alpha=0.2, edgecolor="")

        # Get limits
        # For y_min we always take the lowest value
        auto_y_min = min(min(min_test[idx]), auto_y_min)

        # For y_max we take the highest value after the test_on_best_train/test starts to change
        init_per = performance[0]
        init_up = max_test[idx][0]
        init_lo = min_test[idx][0]
        init_idx = 0
        # Find out when test_on_best_train/test changes
        while init_idx < len(performance) and init_per == performance[init_idx] and \
                init_up == max_test[idx][init_idx] and init_lo == min_test[idx][init_idx]:
            # stop when test_on_best_train/test changes
            init_idx += 1

        # Found the first change, but show two more points on the left side
        init_idx = max(0, init_idx-3)
        if init_idx >= 0:
            auto_x_min = min(times[init_idx], auto_x_min)
        auto_y_max = max(max(max_test[idx][init_idx:]), auto_y_max)
    auto_x_max = times[-1]

    # Label axes
    if log:
        ax1.set_ylabel("log10(Performance)")
    else:
        ax1.set_ylabel("Performance")

    ax1.set_xlabel("log10(time) [sec]")

    # Set axes limits
    ax1.set_xscale("log")
    if y_max is None and y_min is not None:
        ax1.set_ylim([y_min, auto_y_max + 0.01*abs(auto_y_max - y_min)])
    elif y_max is not None and y_min is None:
        ax1.set_ylim([auto_y_min - 0.01*abs(y_max - auto_y_min), y_max])
    elif y_max > y_min and y_max is not None and y_min is not None:
        ax1.set_ylim([y_min, y_max])
    else:
        ax1.set_ylim([auto_y_min-0.01*abs((auto_y_max - auto_y_min)), auto_y_max+0.01*abs((auto_y_max - auto_y_min))])

    if x_max is None and x_min is not None:
        ax1.set_xlim([x_min - 0.1*abs(x_min), auto_x_max + 0.1*abs(auto_x_max)])
    elif x_max is not None and x_min is None:
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min), x_max - 0.1*abs(x_max)])
    elif x_max > x_min and x_max is not None and x_min is not None:
        ax1.set_xlim([x_min, x_max])
    else:
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min), auto_x_max + 0.1*abs(auto_x_max)])

    leg = ax1.legend(loc='best', fancybox=True)
    leg.get_frame().set_alpha(0.5)

    # Save or show figure
    tight_layout()
    subplots_adjust(top=0.85)
    if save != "":
        savefig(save, dpi=100, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.1)
    else:
        show()


def get_test_of_best_train(train, test):
    # get argmin of test performance and return test performance at this idx
    idx = np.argmin(train, 0)
    return [test[idx[row], row] for row in range(len(idx))]


def main():
    prog = "python plot_test_of_best_train.py <WhatIsThis> one/or/many/*ClassicValidationResults*.csv"
    description = "Plot a test error of best training trial"

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

    args, unknown = parser.parse_known_args()

    if len(unknown) < 2:
        print "To less arguments given"
        print(parser.usage)
        sys.exit(1)

    sys.stdout.write("Found " + str(len(unknown)) + " arguments\n")

    # Get files and names
    file_list, name_list = load_data.get_file_and_name_list(unknown, match_file='.csv')
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i in range(len(name_list))]

    # Get data from csv
    train_performance = list()
    test_performance = list()
    time_ = list()
    for name in range(len(name_list)):
        # We have a new experiment
        train_performance.append(list())
        test_performance.append(list())
        for fl in file_list[name]:
            _none, csv_data = load_data.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)
            # Replace too high values with args.maxint
            train_performance[-1].append([min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 1]])
            test_performance[-1].append([min([args.maxvalue, float(i.strip())]) for i in csv_data[:, 2]])
            time_.append([float(i.strip()) for i in csv_data[:, 0]])
            # Check whether we have the same times for all runs
            if len(time_) == 2:
                if time_[0] == time_[1]:
                    time_ = [time_[0], ]
                else:
                    raise NotImplementedError(".csv are not using the same times")

    train_performance = [np.array(i) for i in train_performance]
    test_performance = [np.array(i) for i in test_performance]
    time_ = np.array(time_).flatten()

    # Now get the test results for the best train performance
    # All arrays are numExp x numTrials
    test_of_best_train = list()
    min_test = list()
    max_test = list()
    for i in range(len(train_performance)):
        test_of_best_train.append(get_test_of_best_train(train_performance[i], test_performance[i]))
        min_test.append(np.min(test_performance[i], 0))
        max_test.append(np.max(test_performance[i], 0))

    save = ""
    if args.save != "":
        save = args.save
        print "Save to %s" % args.save
    else:
        print "Show"
    plot_optimization_trace(times=time_, performance_list=test_of_best_train, min_test=min_test, max_test=max_test,
                            name_list=name_list, title=args.title, log=args.log, save=save, y_min=args.ymin,
                            y_max=args.ymax, x_min=args.xmin, x_max=args.xmax)

if __name__ == "__main__":
    main()