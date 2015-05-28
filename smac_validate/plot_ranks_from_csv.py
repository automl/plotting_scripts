#!/usr/bin/env python
from argparse import ArgumentParser
from collections import OrderedDict
import csv
import itertools
import scipy.stats
import sys

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show
import matplotlib.gridspec
import numpy as np

import load_data
import merge_test_performance_different_times as merge


def calculate_ranking(performances, estimators, bootstrap_samples=500):
    num_steps = len(performances[estimators[0]]["performances"][0])
    num_estimators = len(estimators)
    ranking = np.zeros((num_steps, len(estimators)), dtype=np.float64)

    rs = np.random.RandomState(1)

    combinations = []
    maximum = [len(performances[name]) for name in estimators]
    for j in range(bootstrap_samples):
        combination = []
        for idx in range(num_estimators):
            combination.append(rs.randint(maximum[idx]))
        combinations.append(np.array(combination))

    # Initializes ranking array
    # Not sure whether we need this
    #for j, est in enumerate(estimators):
    #    ranking[0][j] = np.mean(range(1, len(estimators) + 1))

    for i in range(ranking.shape[0]):
        num_products = 0

        for combination in combinations:
            ranks = scipy.stats.rankdata(
                [np.round(
                    performances[estimators[idx]]["performances"][number][i], 5)
                 for idx, number in enumerate(combination)])
            num_products += 1
            for j, est in enumerate(estimators):
                ranking[i][j] += ranks[j]

        for j, est in enumerate(estimators):
            ranking[i][j] = ranking[i][j] / num_products

    return list(np.transpose(ranking)), estimators


def plot_optimization_trace(time_list, performance_list, title, name_list,
                            logy=False, logx=False, save="",
                            y_min=None, y_max=None, x_min=None, x_max=None):
    markers = itertools.cycle(['o', 'x', '^', '*'])
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
        marker = markers.next()
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
                 linestyle=linestyles, marker=marker, label=name_list[idx])

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
        ax1.set_ylim([auto_y_min - 0.01*abs(auto_y_max - auto_y_min),
                      auto_y_max + 0.01*abs(auto_y_max - auto_y_min)])

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
    prog = "python plot_ranks_from_csv.py <Dataset> <model> " \
           "*.csv ... "
    description = "Plot ranks over different datasets"

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
                        default="",
                        help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=sys.maxint,
                        help="Replace all values higher than this?")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")

    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print "To less arguments given"
        parser.print_help()
        sys.exit(1)

    # Get files and names
    file_list, name_list = load_data.get_file_and_name_list(unknown,
                                                            match_file='.csv',
                                                            len_name=2)
    for idx in range(len(name_list)):
        assert len(file_list[idx]) == 1
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    dataset_dict = OrderedDict()
    estimator_list = set()
    dataset_list = set()
    for idx, desc in enumerate(name_list):
        dataset = desc[0]
        est = desc[1]
        estimator_list.add(est)
        dataset_list.add(dataset)
        if dataset not in dataset_dict:
            dataset_dict[dataset] = OrderedDict()
        t = None
        p = None
        print "Processing %s, %s" % (dataset, est)
        fh = open(file_list[idx][0], 'r')
        reader = csv.reader(fh)
        for row in reader:
            if t is None:
                # first row
                p = list([list() for i in range(len(row)-1)])
                t = list()
                dataset_dict[dataset][est] = OrderedDict()
                continue
            t.append(float(row[0]))
            del row[0]
            [p[i].append(float(row[i])) for i in range(len(row))]
        dataset_dict[dataset][est]["times"] = [t for i in range(len(p))]
        dataset_dict[dataset][est]["performances"] = p

    # Make lists
    estimator_list = sorted(list(estimator_list))
    dataset_list = list(dataset_list)

    print "Found datasets: %s" % str(dataset_list)
    print "Found estimators: %s" % str(estimator_list)

    for dataset in dataset_list:
        print "Processing dataset: %s" % dataset
        if dataset not in dataset_dict:
            # This should never happen
            raise ValueError("Dataset %s lost" % dataset)

        # We have a list of lists of lists, but we need a list of lists
        tmp_p_list = list()
        tmp_t_list = list()
        len_list = list()       # holds num of arrays for each est
        for est in estimator_list:
            # put all performances in one list = flatten
            if est not in dataset_dict[dataset]:
                raise ValueError("Estimator %s is not given for dataset %s" %
                                 (est, dataset))
            len_list.append(len(dataset_dict[dataset][est]["performances"]))
            tmp_p_list.extend(dataset_dict[dataset][est]["performances"])
            tmp_t_list.extend(dataset_dict[dataset][est]["times"])

        # sanity check
        assert len(tmp_t_list) == len(tmp_p_list)
        assert len(tmp_t_list[0]) == len(tmp_p_list[0])
        p, t = merge.fill_trajectory(performance_list=tmp_p_list,
                                     time_list=tmp_t_list)

        # Now we can refill the dict using len_list as it tells us
        # which arrays belong to which estimator
        for idx, est in enumerate(estimator_list):
            dataset_dict[dataset][est]['performances'] = p[:len_list[idx]]
            # sanity check
            assert len(dataset_dict[dataset][est]['performances'][0]) == len(t)
            del p[:len_list[idx]]
        dataset_dict[dataset]['time'] = t

    # Calculate rankings
    ranking_list = list()
    time_list = list()
    for dataset in dataset_list:
        ranking, e_list = calculate_ranking(performances=dataset_dict[dataset],
                                            estimators=estimator_list)
        ranking_list.extend(ranking)
        assert len(e_list) == len(estimator_list)
        time_list.extend([dataset_dict[dataset]["time"] for i in range(len(e_list))])

    # Fill trajectories as ranks are calculated on different time steps
    # sanity check
    assert len(ranking_list) == len(time_list)
    assert len(ranking_list[0]) == len(time_list[0]), "%d is not %d" % \
                                                      (len(ranking_list[0]),
                                                       len(time_list[0]))
    p, times = merge.fill_trajectory(performance_list=ranking_list,
                                     time_list=time_list)
    del ranking_list, dataset_dict

    performance_list = [list() for e in estimator_list]
    time_list = [times for e in estimator_list]
    for idd, dataset in enumerate(dataset_list):
        for ide, est in enumerate(estimator_list):
            performance_list[ide].append(p[idd*(len(estimator_list))+ide])

    save = ""
    if args.save != "":
        save = args.save
        print "Save to %s" % args.save
    else:
        print "Show"
    plot_optimization_trace(time_list=time_list, performance_list=performance_list,
                            title=args.title, name_list=estimator_list,
                            logy=args.logy, logx=args.logx, save=save,
                            y_min=args.ymin, y_max=args.ymax, x_min=args.xmin,
                            x_max=args.xmax)


if __name__ == "__main__":
    main()