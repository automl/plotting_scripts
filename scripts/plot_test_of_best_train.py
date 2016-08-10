#!/usr/bin/env python

from argparse import ArgumentParser
import sys
import itertools

from matplotlib.pyplot import figure, subplot, rc
import matplotlib.gridspec
import numpy as np

from plottingscripts.utils import read_util, plot_util


def plot_optimization_trace(times, performance_list, title, min_test, max_test,
                            name_list, logy=False, logx=False,
                            y_min=None, y_max=None,
                            x_min=None, x_max=None, ylabel="Loss",
                            properties=None):
    # To use LaTeX
    rc('text', usetex=True)

    # complete properties
    if properties is None:
        properties = dict()
    properties['markers'] = itertools.cycle(['o', 's', '^', '*'])
    properties = plot_util.fill_with_defaults(properties)
    properties["linestyles"] = plot_util.get_plot_linestyles()

    # Hack to not use black
    properties["colors"].next()

    # Set up figure
    ratio = 5
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=int(properties['dpi']))

    ax1 = subplot(gs[0:ratio, :])
    ax1.grid(True, linestyle='-', which='major', color=properties["gridcolor"],
             alpha=float(properties["gridalpha"]))

    if title is not None:
        fig.suptitle(title, fontsize=int(properties["titlefontsize"]))

    # set initial limits
    auto_y_min = sys.maxint
    auto_y_max = -sys.maxint
    auto_x_min = sys.maxint

    for idx, performance in enumerate(performance_list):
        if logy:
            performance = np.log10(performance)
            min_test[idx] = np.log10(min_test[idx])
            max_test[idx] = np.log10(max_test[idx])

        color = properties["colors"].next()
        marker = properties["markers"].next()
        linestyle = properties["linestyles"].next()

        ax1.plot(times, performance, color=color,
                 linewidth=int(properties["linewidth"]),
                 markersize=int(properties["markersize"]),
                 linestyle=linestyle, marker=marker, label=name_list[idx])
        #ax1.fill_between(times, min_test[idx], max_test[idx], facecolor=color,
        #                 alpha=0.2, edgecolor="")

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
    if logy:
        ax1.set_ylabel(r"log10(%s)" % ylabel, fontsize=properties["labelfontsize"])
    else:
        ax1.set_ylabel(r"%s" % ylabel, fontsize=properties["labelfontsize"])

    if logx:
        ax1.set_xscale("log")
        auto_x_min = max(0.1, auto_x_min)
    ax1.set_xlabel("time [sec]", fontsize=properties["labelfontsize"])

    # Set axes limits
    if y_max is None and y_min is not None:
        ax1.set_ylim([y_min, auto_y_max + 0.01*abs(auto_y_max - y_min)])
    elif y_max is not None and y_min is None:
        ax1.set_ylim([auto_y_min - 0.01*abs(y_max - auto_y_min), y_max])
    elif y_max > y_min and y_max is not None and y_min is not None:
        ax1.set_ylim([y_min, y_max])
    else:
        ax1.set_ylim([auto_y_min-0.01*abs((auto_y_max - auto_y_min)),
                      auto_y_max + 0.01*abs((auto_y_max - auto_y_min))])

    if x_max is None and x_min is not None:
        ax1.set_xlim([x_min - 0.1*abs(x_min), auto_x_max + 0.1*abs(auto_x_max)])
    elif x_max is not None and x_min is None:
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min), x_max - 0.1*abs(x_max)])
    elif x_max > x_min and x_max is not None and x_min is not None:
        ax1.set_xlim([x_min, x_max])
    else:
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min),
                      auto_x_max + 0.1*abs(auto_x_max)])

    leg = ax1.legend(loc='best', fancybox=True, frameon=False,
                     prop={'size': int(properties["legendsize"])})
    leg.get_frame().set_alpha(0.5)

    return fig


def get_test_of_best_train(train, test):
    # get argmin of test performance and return test performance at this idx
    idx = np.argmin(train, 0)
    return [test[idx[row], row] for row in range(len(idx))]


def main():
    prog = "python plot_test_of_best_train.py <WhatIsThis> one/or/many/" \
           "*ClassicValidationResults*.csv"
    description = "Plot a test error of best training trial"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    parser.add_argument("--logy", action="store_true", dest="logy",
                        default=False,
                        help="Plot y-axis on on log scale")
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
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint,
                        help="Replace all values higher than this?")
    parser.add_argument("--ylabel", dest="ylabel", default="loss",
                        help="Label on y-axis")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))
    args, unknown = parser.parse_known_args()

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    sys.stdout.write("Found " + str(len(unknown)) + " arguments\n")

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv')
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i
                     in range(len(name_list))]

    # Get data from csv
    train_performance = list()
    test_performance = list()
    time_ = list()
    for name in range(len(name_list)):
        # We have a new experiment
        train_performance.append(list())
        test_performance.append(list())
        for fl in file_list[name]:
            _none, csv_data = read_util.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)
            # Replace too high values with args.maxint
            train_performance[-1].append([min([args.maxvalue, float(i.strip())])
                                          for i in csv_data[:, 1]])
            test_performance[-1].append([min([args.maxvalue, float(i.strip())])
                                         for i in csv_data[:, 2]])
            time_.append([float(i.strip()) for i in csv_data[:, 0]])
            # Check whether we have the same times for all runs
            if len(time_) == 2:
                if time_[0] == time_[1]:
                    time_ = [time_[0], ]
                else:
                    raise NotImplementedError(".csv's do not use the same "
                                              "timesteps")

    train_performance = [np.array(i) for i in train_performance]
    test_performance = [np.array(i) for i in test_performance]
    time_ = np.array(time_).flatten()

    # Now get the test results for the best train performance
    # All arrays are numExp x numTrials
    test_of_best_train = list()
    min_test = list()
    max_test = list()
    for i in range(len(train_performance)):
        test_of_best_train.append(get_test_of_best_train(train_performance[i],
                                                         test_performance[i]))
        min_test.append(np.min(test_performance[i], 0))
        max_test.append(np.max(test_performance[i], 0))

    prop = {}
    args_dict = vars(args)
    for key in defaults:
        prop[key] = args_dict[key]

    fig = plot_optimization_trace(times=time_,
                                  performance_list=test_of_best_train,
                                  min_test=min_test, max_test=max_test,
                                  name_list=name_list, title=args.title,
                                  logy=args.logy, logx=True, properties=prop,
                                  y_min=args.ymin, y_max=args.ymax,
                                  x_min=args.xmin, x_max=args.xmax,
                                  ylabel=args.ylabel)
    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()

if __name__ == "__main__":
    main()
