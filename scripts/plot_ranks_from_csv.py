#!/usr/bin/env python
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import OrderedDict
import csv
import scipy.stats
import sys
import warnings

import numpy as np

from plottingscripts.utils import read_util
from plottingscripts.utils import plot_util
from plottingscripts.utils.merge_test_performance_different_times import \
    fill_trajectory
import plottingscripts.plotting.plot_methods as plot_methods


def read_data(file_list, name_list):
    dataset_dict = OrderedDict()
    estimator_list = set()
    dataset_list = set()

    to_skip = set()

    for idx, desc in enumerate(name_list):
        dataset = desc[0]
        est = desc[1]
        estimator_list.add(est)

        trajectories = []
        times_ = []
        # print("Processing %s" % est)
        for csv_file in file_list[idx]:
            # print(file_list[idx][0])
            fh = open(csv_file, 'r')
            reader = csv.reader(fh)
            p = list()
            t = list()
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                if float(row[0]) < 0:
                    warnings.warn('Found time stamp < 0 in file %s' % csv_file)
                    continue
                try:
                    t.append(float(row[0]))
                    p.append(float(row[2]))
                except IndexError:
                    print('IndexError reading %s at line %d: %s' %
                          (csv_file, i, row))
                    raise

            if len(t) == 0:
                print('Found empty file %s' % csv_file)
                continue

            times_.append(t)
            trajectories.append(p)

        if len(trajectories) != len(file_list[idx]):
            to_skip.add(dataset)
            continue

        trajectories, times_ = fill_trajectory(trajectories, times_)

        dataset_list.add(dataset)
        if dataset not in dataset_dict:
            dataset_dict[dataset] = OrderedDict()
        if est not in dataset_dict[dataset]:
            dataset_dict[dataset][est] = OrderedDict()

        dataset_dict[dataset][est]["times"] = times_
        dataset_dict[dataset][est]["performances"] = trajectories

    max_num_keys = max([len(dataset_dict[dataset]) for dataset in dataset_dict])
    for dataset in dataset_dict:
        if len(dataset_dict[dataset]) != max_num_keys:
            to_skip.add(dataset)

    for dataset in to_skip:
        print('Skipping dataset %s' % dataset)
        try:
            del dataset_dict[dataset]
        except:
            pass
        try:
            dataset_list.remove(dataset)
        except:
            pass
    return dataset_dict, dataset_list, estimator_list


def calculate_ranking(performances, estimators, bootstrap_samples=500):
    num_steps = len(performances[estimators[0]]["performances"][0])
    num_estimators = len(estimators)
    ranking = np.zeros((num_steps, len(estimators)), dtype=np.float64)

    rs = np.random.RandomState(1)

    combinations = []
    maximum = [len(performances[name]["performances"]) for name in estimators]
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


def main():
    prog = "python plot_ranks_from_csv.py <Dataset> <model> " \
           "*.csv ... "
    description = "Plot ranks over different datasets"

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
                        default="",
                        help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")
    parser.add_argument("--samples", dest="samples", type=int,
                        default=10, help="Number of bootstrap samples to plot")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))

    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print("To less arguments given")
        parser.print_help()
        sys.exit(1)

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv',
                                                            len_name=2)
    for idx in range(len(name_list)):
        assert len(file_list[idx]) == 1, "%s" % file_list[idx]
        print("%20s contains %d file(s)" %
              (name_list[idx], len(file_list[idx])))

    dataset_dict, dataset_list, estimator_list = read_data(file_list, name_list)# Make lists
    estimator_list = sorted(list(estimator_list))
    dataset_list = sorted(list(dataset_list))

    print("Found datasets: %s" % str(dataset_list))
    print("Found estimators: %s" % str(estimator_list))

    for dataset in dataset_list:
        # In order to use fill trajectory for all runs on one dataset,
        # the trajectories for each run need to be in one array -> flatten the
        # array and put it together afterwards

        print("Processing dataset: %s" % dataset)
        if dataset not in dataset_dict:
            # This should never happen
            raise ValueError("Dataset %s lost" % dataset)

        # Merge the times of this dataset
        performances_per_estimator = list()
        times_per_estimator = list()
        num_performances_per_estimator = list()
        for est in dataset_dict[dataset]:
            num_performances = len(dataset_dict[dataset][est]['performances'])
            num_performances_per_estimator.extend([est] * num_performances)
            performances_per_estimator.extend(dataset_dict[dataset][est]['performances'])
            times_per_estimator.extend(
                [dataset_dict[dataset][est]['times']] * num_performances)

        performances, times = fill_trajectory(
            performance_list=performances_per_estimator,
            time_list=times_per_estimator)

        assert performances.shape[0] == times.shape[0], \
            (performances.shape[0], times.shape[0])

        for i, est in enumerate(dataset_dict[dataset]):
            dataset_dict[dataset][est]['performances'] = list()
            dataset_dict[dataset][est]['times'] = list()

        for est, perf in zip (num_performances_per_estimator,
                              performances.transpose()):
            dataset_dict[dataset][est]['performances'].append(perf)
            dataset_dict[dataset][est]['times'].append(times)

    # Calculate rankings
    ranking_list = list()
    time_list = list()
    for dataset in dataset_list:

        ranking, e_list = calculate_ranking(performances=dataset_dict[dataset],
                                            estimators=estimator_list,
                                            bootstrap_samples=args.samples)

        ranking_list.extend(ranking)
        assert len(e_list) == len(estimator_list)
        time_list.extend([dataset_dict[dataset][e]["times"][0] for e in e_list])

    # Fill trajectories as ranks are calculated on different time steps
    # sanity check
    assert len(ranking_list) == len(time_list), (len(ranking_list),
                                                 len(time_list))
    assert len(ranking_list[0]) == len(time_list[0]), "%d is not %d" % \
                                                      (len(ranking_list[0]),
                                                       len(time_list[0]))
    p, times = fill_trajectory(performance_list=ranking_list,
                               time_list=time_list)
    del ranking_list, dataset_dict
    p = p.transpose()

    performance_list = [list() for e in estimator_list]
    time_list = [times for e in estimator_list]
    for idd, dataset in enumerate(dataset_list):
        for ide, est in enumerate(estimator_list):
            performance_list[ide].append(p[idd*(len(estimator_list))+ide])

    for entry in performance_list:
        assert np.array(entry).shape[1] == time_list[0].shape[0], \
            (np.array(entry).shape[1], time_list[0].shape)

    prop = {}
    args_dict = vars(args)
    for key in defaults:
        prop[key] = args_dict[key]
    #prop['linestyles'] = itertools.cycle(["-", ":"])

    fig = plot_methods.plot_optimization_trace_mult_exp(
        time_list=time_list, performance_list=performance_list,
        title=args.title, name_list=estimator_list, logy=args.logy,
        logx=args.logx, y_min=args.ymin, y_max=args.ymax,
        x_min=args.xmin, x_max=args.xmax,
        ylabel="average rank (%d bootstrap samples)" % args.samples,
        scale_std=0, properties=prop)

    if args.save != "":
        print("Save plot to %s" % args.save)
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()


if __name__ == "__main__":
    main()