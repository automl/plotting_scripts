#!/usr/bin/env python

from argparse import ArgumentParser
import sys
import itertools

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show
import matplotlib.gridspec
import numpy as np

import load_data


def plot_scatter_plot(x_data, y_data, labels, title="", save="", debug=False,
                      min_val=None, max_val=1000, grey_factor=1, linefactors=None):
    regular_marker = '+'
    timeout_marker = '+'
    grey_marker = 'x'
    c_angle_bisector = "#e41a1c" # Red
    c_good_points = "#999999"    # Grey
    c_other_points = "k"

    st_ref = "--"

    # # Colors
    ref_colors = itertools.cycle([ # "#e41a1c",    # Red
                                  "#377eb8",    # Blue
                                  "#4daf4a",    # Green
                                  "#984ea3",    # Purple
                                  "#ff7f00",    # Orange
                                  "#ffff33",    # Yellow
                                  "#a65628",    # Brown
                                  "#f781bf",    # Pink
                                   # "#999999",    # Grey
    ])

    # Set up figure
    ratio = 1
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=100)
    fig.suptitle(title, fontsize=16)
    ax1 = subplot(gs[0:ratio, :], aspect='equal')
    ax1.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

    # set initial limits
    if min_val is not None:
        auto_min_val = min([min(x_data), min(y_data), min_val])
    else:
        auto_min_val = min([min(x_data), min(y_data)])
    auto_max_val = max_val

    # Plot angle bisector and reference_lines
    out_up = auto_max_val
    out_lo = auto_min_val

    ax1.plot([out_lo, out_up], [out_lo, out_up], c=c_angle_bisector)

    if linefactors is not None:
        for f in linefactors:
            c = ref_colors.next()
            # Lower reference lines
            ax1.plot([f*out_lo, out_up], [out_lo, (1.0/f)*out_up], c=c, linestyle=st_ref)
            # Upper reference lines
            ax1.plot([out_lo, (1.0/f)*out_up], [f*out_lo, out_up], c=c, linestyle=st_ref)
            if debug:
                ax1.text((1.0/f)*out_up, out_up, "%2.1fx" % f, color=c, fontsize=10)
                ax1.text(out_up, (1.0/f)*out_up, "%2.1fx" % f, color=c, fontsize=10)


    # Scatter
    grey_idx = list()
    timeout_x = list()
    timeout_y = list()
    timeout_both = list()
    rest_idx = list()
    for idx_x, x in enumerate(x_data):
        if x > max_val > y_data[idx_x]:
            # timeout of x algo
            timeout_x.append(idx_x)
        elif y_data[idx_x] > max_val > x:
            # timeout of y algo
            timeout_y.append(idx_x)
        elif y_data[idx_x] > max_val and x > max_val:
            # timeout of both algos
            timeout_both.append(idx_x)
        elif y_data[idx_x] < grey_factor*x and x < grey_factor*y_data[idx_x]:
            grey_idx.append(idx_x)
        else:
            rest_idx.append(idx_x)

    # Regular points
    ax1.scatter(x_data[grey_idx], y_data[grey_idx], marker=grey_marker, c=c_good_points)
    ax1.scatter(x_data[rest_idx], y_data[rest_idx], marker=regular_marker, c=c_other_points)

    # Timeout points
    timeout_val = 10**int(np.log10(10*max_val))
    ax1.scatter([timeout_val]*len(timeout_x), y_data[timeout_x], marker=timeout_marker, c=c_other_points)
    ax1.scatter([timeout_val]*len(timeout_both), [timeout_val]*len(timeout_both), marker=timeout_marker, c=c_other_points)
    ax1.scatter(x_data[timeout_y], [timeout_val]*len(timeout_y), marker=timeout_marker, c=c_other_points)
    # Timeout line
    ax1.plot([timeout_val, timeout_val], [auto_min_val, timeout_val], c=c_other_points, linestyle=":")
    ax1.plot([auto_min_val, timeout_val], [timeout_val, timeout_val], c=c_other_points, linestyle=":")

    if debug:
        # debug option
        ax1.scatter(x_data, y_data, marker="o", facecolor="", s=50, label="original data")

    # Set axes scale and limits
    ax1.set_xscale("log")
    ax1.set_yscale("log")

    max_val *= 1.5
    auto_min_val *= 0.9
    if max_val is None and min_val is not None:
        # User sets min_val
        ax1.set_ylim([min_val, 10*max_val])
        ax1.set_xlim(ax1.get_ylim())
    elif max_val is not None and min_val is None:
        # User sets max val
        ax1.set_ylim([auto_min_val, 10*max_val])
        ax1.set_xlim(ax1.get_ylim())
    elif max_val > min_val and max_val is not None and min_val is not None:
        # User sets both, min and max -val
        ax1.set_ylim([min_val, 10*max_val])
        ax1.set_xlim(ax1.get_ylim())
    else:
        # User sets nothing
        ax1.set_xlim([auto_min_val, 10*max_val])
        ax1.set_ylim(ax1.get_xlim())

    # Set axes labels
    ax1.set_xlabel(labels[0])
    ax1.set_ylabel(labels[1])

    new_ticks_x = ax1.get_xticks()[:-2]
    new_ticks_label = list(new_ticks_x)
    for l_idx in range(len(new_ticks_label)):
        if new_ticks_label[l_idx] >= 1:
            new_ticks_label[l_idx] = int(new_ticks_label[l_idx])
    new_ticks_label.append("timeout")
    ax1.set_xticklabels(new_ticks_label)  # , rotation=45)
    ax1.set_yticklabels(new_ticks_label)  # , rotation=45)

    if debug:
        # Plot legend
        leg = ax1.legend(loc='best', fancybox=True)
        leg.get_frame().set_alpha(0.5)

    # Remove top and right line
    # spines_to_remove = ['top', 'right']
    # for spine in spines_to_remove:
    #     ax1.spines[spine].set_visible(False)
    # ax1.get_xaxis().tick_bottom()
    # ax1.get_yaxis().tick_left()

    # Save or show figure
    tight_layout()
    subplots_adjust(top=0.85)
    if save != "":
        savefig(save, dpi=100, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.1)
    else:
        show()


def main():
    prog = "python plot_scatter.py any.csv"
    description = "Plots performances of the best config at one time vs another in a scatter plot"

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
                        default=None, help="Plot X speedup/slowdown, format 'X,..,X' (no spaces)")
    parser.add_argument("--time", dest="time", default=None,
                        help="Plot config at which time?, format 'time1,time2' ")
    parser.add_argument("--obj", dest="obj", default=None,
                        help="Path to validationObjectiveMatrix-traj-run-* file")
    parser.add_argument("--res", dest="res", required=True,
                        help="Path to validationResults-traj-run-* file")

    args, unknown = parser.parse_known_args()

    if len(unknown) != 0:
        print "Wrong number of arguments"
        parser.print_help()
        sys.exit(1)

    if args.grey_factor < 1:
        print "A grey-factor lower than one makes no sense"
        parser.print_help()
        sys.exit(1)

    # Load validationResults
    res_header, res_data = load_data.read_csv(args.res, has_header=True)
    av_times = [int(float(row[0])) for row in res_data if row[len(res_header)-2] != '"1"']
    if args.time == None:
        # Print available times and quit
        print "Choose a time from"
        print "\n".join(["* %s" % i for i in av_times])
        sys.exit(0)
    time_arr = args.time.split(",")
    if len(time_arr) != 2:
        print "Something wrong with %s, should be 'a,b'" % args.time
    time_1 = float(time_arr[0])
    time_2 = float(time_arr[1])
    #print time_1
    #print time_2
    #print res_data
    #print res_data

    if args.obj == None:
        print "Missing --obj"
        parser.print_help()
        sys.exit(1)

    # Now extract data
    config_1 = [int(float(row[len(res_header)-2].strip('"'))) for row in res_data if float(row[0]) == time_1]
    config_2 = [int(float(row[len(res_header)-2].strip('"'))) for row in res_data if float(row[0]) == time_2]
    if len(config_1) != 1 or len(config_2) != 1:
        print "Time %s or %s not found. Choose a time from:" % (time_1, time_2)
        print "\n".join(["* %s" % i for i in av_times])
        sys.exit(1)
    config_1 = config_1[0]
    config_2 = config_2[0]


    obj_header, obj_data = load_data.read_csv(args.obj, has_header=True)
    head_template = '"Objective of validation config #%s"'
    idx_1 = obj_header.index(head_template % config_1)
    idx_2 = obj_header.index(head_template % config_2)
    #print idx_1, idx_2

    data_one = np.array([float(row[idx_1].strip('"')) for row in obj_data])
    data_two = np.array([float(row[idx_2].strip('"')) for row in obj_data])
    #print data_one
    #print data_two

    print "Found %s points for config %d and %s points for config %d" % (str(data_one.shape), config_1, str(data_two.shape), config_2)

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

    save = ""
    if args.save != "":
        save = args.save
        print "Save to %s" % args.save
    else:
        print "Show"
    plot_scatter_plot(x_data=data_one, y_data=data_two, labels=[head_template % config_1, head_template % config_2], title=args.title, save=save,
                      max_val=args.max, min_val=args.min, grey_factor=args.grey_factor,
                      linefactors=linefactors, debug=args.verbose)


if __name__ == "__main__":
    main()