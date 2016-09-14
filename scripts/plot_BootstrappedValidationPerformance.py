#!/usr/bin/env python

from argparse import ArgumentParser
import os
import sys

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from plottingscripts.utils import read_util, plot_util, helper
import plottingscripts.plotting.plot_methods as plot_methods
import plottingscripts.utils.macros


def main():
    prog = "python plot_BootstrappedValidationPerformance.py <WhatIsThis> " \
           "one/or/many/*ClassicValidationResults*.csv"
    description = "Plot a median trace with quantiles for multiple experiments"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    parser.add_argument("--logx", action="store_true", dest="logx",
                        default=False, help="Plot x-axis on log scale")
    parser.add_argument("--logy", action="store_true", dest="logy",
                        default=False, help="Plot y-axis on log scale")
    parser.add_argument("--ymax", dest="ymax", type=float,
                        default=None, help="Maximum of the y-axis")
    parser.add_argument("--ymin", dest="ymin", type=float,
                        default=None, help="Minimum of the y-axis")
    parser.add_argument("--xmax", dest="xmax", type=float,
                        default=None, help="Maximum of the x-axis")
    parser.add_argument("--xmin", dest="xmin", type=float,
                        default=None, help="Minimum of the x-axis")
    parser.add_argument("--ylabel", dest="ylabel", default=None,
                        help="Label on y-axis")
    parser.add_argument("-s", "--save", dest="save",
                        default="", help="Where to save plot instead of "
                                         "showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("--maxvalue", dest="maxvalue", type=float,
                        default=plottingscripts.utils.macros.MAXINT,
                        help="Replace all values higher than this?")
    parser.add_argument("--agglomeration", dest="agglomeration", type=str,
                        default="median", choices=("median", "mean"),
                        help="Plot mean or median")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False,
                        help="print number of runs on plot")
    parser.add_argument("-b", "--bootstrap", dest="bootstrap", default="10x8",
                        help="n*m; For each non-GGA experiment draw n times m "
                             "trajectories and plot best of train")
    parser.add_argument("--seed", default=None, type=int, dest="seed",
                        help="Seed for reproducibility."
                             "Will be used for every Bootstrap sampling")

    # Properties
    # We need this to show defaults for -h
    defaults = plot_util.get_defaults()
    for key in defaults:
        parser.add_argument("--%s" % key, dest=key, default=None,
                            help="%s, default: %s" % (key, str(defaults[key])))
    args, unknown = parser.parse_known_args()

    sys.stdout.write("\nFound " + str(len(unknown)) + " arguments\n")

    # Calc bootstrap samples
    bootstrap_repetitions, bootstrap_samples = [int(i) for i
                                                in args.bootstrap.split("x")]
    print("[BOOTSTRAP] Do %d repetition with %d samples each" %
          (bootstrap_repetitions, bootstrap_samples))

    if len(unknown) < 2:
        print("To less arguments given")
        parser.print_help()
        sys.exit(1)

    args.ylabel = "%s performance on test instances" % args.agglomeration

    # Set up properties
    prop = {}
    args_dict = vars(args)
    for key in defaults:
        prop[key] = args_dict[key]

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown,
                                                            match_file='.csv')
    for idx in range(len(name_list)):
        print("%20s contains %d file(s)" %
              (name_list[idx], len(file_list[idx])))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i
                     in range(len(name_list))]

    # Get data from csv
    performance = list()
    time_ = list()
    show_from = -plottingscripts.utils.macros.MAXINT

    for name in range(len(name_list)):
        # We have a new experiment
        tmp_tst_perf_list = list()
        tmp_trn_perf_list = list()
        for fl in file_list[name]:
            _none, csv_data = read_util.read_csv(fl, has_header=True)
            csv_data = np.array(csv_data)

            # Replace too high values with args.maxint
            # Although we only care about test, we need both for bootstrapping
            trn_data = [min([args.maxvalue, float(i.strip())]) for i
                        in csv_data[:, 1]]
            tst_data = [min([args.maxvalue, float(i.strip())]) for i
                        in csv_data[:, 2]]

            # Do we have only non maxint data?
            show_from = max(tst_data.count(args.maxvalue), show_from)
            tmp_tst_perf_list.append(tst_data)
            tmp_trn_perf_list.append(trn_data)
            time_.append([float(i.strip()) for i in csv_data[:, 0]])
            # Check whether we have the same times for all runs
            if len(time_) == 2:
                if time_[0] == time_[1]:
                    time_ = [time_[0], ]
                else:
                    raise NotImplementedError(".csv are not using the same "
                                              "timesteps")
        tmp_trn_perf_list = np.array(tmp_trn_perf_list)
        tmp_tst_perf_list = np.array(tmp_tst_perf_list)

        # If not GGA draw bootstrap samples
        if "GGA" not in name_list[name]:
            print("Bootstrap %s" % name_list[name])
            new_performance = np.zeros([bootstrap_repetitions,
                                        tmp_tst_perf_list.shape[1]])
            for t in range(tmp_tst_perf_list.shape[1]):
                # for each timestep
                for i in range(bootstrap_repetitions):
                    # for each repetition (='pseudo' run)
                    # sample #bootstrap-sample-size idxs
                    sample_idx = helper.bootstrap_sample_idx(
                            num_samples=len(tmp_tst_perf_list),
                            boot_strap_size=bootstrap_samples, rng=args.seed)
                    # then get test value of best train
                    best_train = np.argmin(tmp_trn_perf_list[sample_idx, t])
                    # and use this as new performance for pseudorun i at time t
                    new_performance[i, t] = tmp_tst_perf_list[best_train, t]
            performance.append(new_performance)
        else:
            performance.append(tmp_tst_perf_list)

    performance = [np.array(i) for i in performance]

    time_ = np.array(time_).flatten()
    print(time_.shape)
    print([p.shape for p in performance])

    if args.xmin is None and show_from != 0:
        args.xmin = show_from

    properties = helper.fill_property_dict(arguments=args, defaults=defaults)

    new_time_list = [time_ for i in range(len(performance))]
    fig = plot_methods.\
        plot_optimization_trace_mult_exp(time_list=new_time_list,
                                         performance_list=performance,
                                         title=args.title,
                                         name_list=name_list,
                                         logx=args.logx,
                                         logy=args.logy,
                                         y_min=args.ymin,
                                         y_max=args.ymax,
                                         x_min=args.xmin,
                                         x_max=args.xmax,
                                         agglomeration=args.agglomeration,
                                         ylabel=args.ylabel,
                                         properties=properties)
    if args.save != "":
        print("Save plot to %s" % args.save)
        plot_util.save_plot(fig, args.save, plot_util.get_defaults()['dpi'])
    else:
        fig.show()

if __name__ == "__main__":
    main()