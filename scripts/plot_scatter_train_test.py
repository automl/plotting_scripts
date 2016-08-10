#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import sys
import collections

import numpy as np

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show, tick_params
import matplotlib.gridspec

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from plottingscripts.utils import read_util, plot_util


def main():
    prog = "python plot_scatter_train_test.py " \
           "RANDOM_train one/or/many/validationResults-cli-*.csv " \
           "RANDOM_test one/or/many/validationResults-cli-*.csv " \
           "SMAC_train one/or/many/validationResults-traj-run-*.csv" \
           "SMAC_test one/or/many/validationResults-traj-run-*.csv"
    description = "Scatter PAR10 on train and test instances "

    parser = ArgumentParser(description=description, prog=prog,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # General Options
    parser.add_argument("--logx", action="store_true", dest="logx",
                        default=False, help="Plot x-axis on log scale")
    parser.add_argument("--logy", action="store_true", dest="logy",
                        default=False, help="Plot y-axis on log scale")
    parser.add_argument("--max", dest="max", type=float,
                        default=None, help="Maximum of the axes")
    parser.add_argument("--min", dest="min", type=float,
                        default=None, help="Minimum of the axes")

    parser.add_argument("-s", "--save", dest="save",
                        default="", help="Where to save plot instead of "
                                         "showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False,
                        help="print number of runs on plot")
    parser.add_argument("--log", dest="log", action="store_true", default=False,
                        help="Set axes to log scale")
    parser.add_argument("--objective", dest="objective", action="store_true",
                        default=False, help="Provide a ObjectiveMatrix instead "
                                            "of RunResults")
    parser.add_argument("--par", dest="par", type=int, default=None,
                        help="Only used for ObjectiveMatrix to calculate PAR "
                             "score")
    parser.add_argument("--cutoff", dest="cutoff", type=int, default=None,
                        help="Only used for ObjectiveMatrix to calculate PAR "
                             "score")
    parser.add_argument("--default", dest="default", default=False,
                        action="store_true", help="If RANDOM given then mark "
                                                  "the first config as default")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))

    args, unknown = parser.parse_known_args()

    if args.objective:
        assert args.cutoff is not None, "If --objective, you need to " \
                                        "set --cutoff"
        assert args.par is not None, "If --objective, you need to set --par"

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv')

    if len(name_list) % 2 != 0:
        raise ValueError("NOT A MULTIPLE OF TWO. ALWAYS NEED TEST AND TRAIN(%s)")

    value_dict = collections.OrderedDict()
    name_ls = []
    min_ = sys.maxint
    max_ = -sys.maxint

    for name in range(len(name_list)):
        base_name = "_".join(name_list[name].split("_")[:-1])
        ext = name_list[name].split("_")[-1]
        assert ext in ("train", "test"), "%s" % name_list[name]
        name_ls.append(base_name)
        value_dict[name_list[name]] = list()
        for fl in file_list[name]:
            if args.objective:
                # We need to parse objective matrix and calc PAR score
                data = read_util.read_validationObjectiveMatrix_file(fl)
                perf = list()
                for cf in data:
                    row = np.array(data[cf])
                    row[row >= args.cutoff] = args.par * args.cutoff
                    perf.append(row)
                perf = np.array(perf)
                value_dict[name_list[name]].append(np.mean(perf, axis=0))
                min_ = np.min((min_, np.min(np.mean(perf, axis=0))))
                max_ = np.max((max_, np.max(np.mean(perf, axis=0))))
            else:
                data = read_util.read_trajectory_file(fl)
                for entry in data:
                    value_dict[name_list[name]].append(
                            entry["Test Set Performance"])
                    min_ = np.min((min_, entry["Test Set Performance"]))
                    max_ = np.max((max_, entry["Test Set Performance"]))
        value_dict[name_list[name]] = np.array(value_dict[name_list[name]]).ravel()
        print value_dict[name_list[name]].shape
    name_ls = set(name_ls)

    ################### Plotting starts here
    ################### TODO: Put in separate folder
    properties = {}
    args_dict = vars(args)
    for key in defaults:
        properties[key] = args_dict[key]
        try:
            properties[key] = float(properties[key])
            if int(properties[key]) == properties[key]:
                properties[key] = int(properties[key])
        except:
            continue
    properties = plot_util.fill_with_defaults(properties)

    size = 1
    # Set up figure
    ratio = 5
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=int(properties['dpi'])) #, figsize=(8, 4))
    ax1 = subplot(gs[0:ratio, :])
    ax1.grid(True, linestyle='-', which='major', color=properties["gridcolor"],
             alpha=float(properties["gridalpha"]))

    for base_name in name_ls:
        if "DEFAULT" in base_name.upper():
            # Do not plot using alpha
            alpha = 1
            zorder = 99
        else:
            alpha = 0.5
            zorder = None
        ax1.scatter(value_dict[base_name + "_train"],
                    value_dict[base_name + "_test"],
                    label=base_name.replace("_", " "),
                    marker=properties["markers"].next(),
                    c=properties["colors"].next(), edgecolor="",
                    s=properties["markersize"], alpha=alpha, zorder=zorder)
        if (base_name.upper() == "RANDOM" and args.default):
            ax1.scatter(value_dict[base_name + "_train"][0],
                        value_dict[base_name + "_test"][0],
                        label="default", marker=properties["markers"].next(),
                        c=properties["colors"].next(), edgecolor="",
                        s=properties["markersize"], alpha=1, zorder=99)
    ax1.legend(loc="lower right", framealpha=1, fancybox=True, ncol=1,
               scatterpoints=1)

    ax1.set_xlabel("PAR10 on training set", fontsize=properties["labelfontsize"])
    ax1.set_ylabel("PAR10 on test set", fontsize=properties["labelfontsize"])
    tick_params(axis='both', which='major', labelsize=properties["ticklabelsize"])

    ax1.plot([0.1, 3500], [0.1, 3500], c='k', zorder=0)
    if args.max is not None:
        if args.min is not None:
            ax1.set_xlim([args.min, args.max])
            ax1.set_ylim([args.min, args.max])
        else:
            ax1.set_xlim([min_, args.max])
            ax1.set_ylim([min_, args.max])
    else:
        if args.min is not None:
            ax1.set_xlim([args.min, max_])
            ax1.set_ylim([args.min, max_])
        else:
            ax1.set_xlim([min_, max_])
            ax1.set_ylim([min_, max_])
    ax1.set_aspect('equal')

    if args.log:
        ax1.set_xscale("log")
        ax1.set_yscale("log")

    if args.save != "":
        print "Save plot to %s" % args.save
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()


if __name__ == "__main__":
    main()