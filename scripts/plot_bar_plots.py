#!/usr/bin/env python
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from plottingscripts.utils import read_util
from plottingscripts.utils import plot_util


def main():
    prog = "python plot_bar_plots.py <Dataset> <model> " \
           "exactly_one_.csv ... "
    description = "Plot bar plots per dataset"

    parser = ArgumentParser(description=description, prog=prog,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # General Options
    parser.add_argument("--logy", action="store_true", dest="logy",
                        default=False, help="Plot y-axis on log scale")
    parser.add_argument("--limit", default=3600.0, type=float, help="Moment in time to assess the quality")
    parser.add_argument("-s", "--save", dest="save",
                        default="",
                        help="Where to save plot instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print number of runs on plot")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))

    args, unknown = parser.parse_known_args()
    limit = args.limit

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    if len(unknown) < 2:
        print("To less arguments given")
        parser.print_help()
        sys.exit(1)

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv',
                                                            len_name=2)

    datasets = set()
    strategies = set()
    strategy_dataset = {}
    for idx in range(len(name_list)):
        dataset = name_list[idx][0]
        strategy = name_list[idx][1]
        datasets.add(dataset)
        strategies.add(strategy)

        if strategy not in strategy_dataset:
            strategy_dataset[strategy] = {}
        strategy_dataset[strategy][dataset] = (dataset, file_list[idx][0])

        assert len(file_list[idx]) == 1, "%s" % file_list[idx]
        print("%20s contains %d file(s)" %
              (name_list[idx], len(file_list[idx])))

    results = {}
    for strategy in strategies:
        means = list()
        labels = []
        for dataset in sorted(strategy_dataset[strategy]):
            loss = 1.0
            dataset_id = strategy_dataset[strategy][dataset][0]
            file_path = strategy_dataset[strategy][dataset][1]
            labels.append(dataset_id)

            with open(file_path, 'r') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for idx, row in enumerate(csvreader):
                    if idx > 0:
                        time = float(row[0])
                        test = float(row[2])
                        if time < limit:
                            loss = test
            means.append(loss)
        results[strategy] = means

    ind = np.arange(len(datasets))  # the x locations for the groups
    width = 0.15  # the width of the bars

    fig, ax = plt.subplots()

    colors = ['r', 'b', 'g']

    rects = []
    legends = []
    for idx, strategy in enumerate(results):
        rects.append(ax.bar(ind + idx * width, results[strategy], width, color=colors[idx]))
        legends.append(strategy)

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Result')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(labels, rotation='vertical')

    ax.legend(rects, legends)

    def autolabel(rects):
        """
        Attach a text label above each bar displaying its height
        """
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                    '%f' % height,
                    ha='center', va='bottom')

    # for rect in rects:
    #    autolabel(rect)

    if args.save != "":
        print("Save plot to %s" % args.save)
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()


if __name__ == "__main__":
    main()