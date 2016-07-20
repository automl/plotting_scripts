import itertools
import sys

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show, tick_params
import matplotlib.gridspec
import numpy as np

import plottingscripts.utils.plot_util as plot_util


def plot_optimization_trace(times, performance_list, title, name_list,
                            logx=True, logy=False, y_min=None, y_max=None,
                            x_min=None, x_max=None, ylabel="performance",
                            properties=None):
    '''
    plots a median optimization trace based one time array
    '''

    # complete properties
    if properties is None:
        properties = dict()
    #properties['markers'] = itertools.cycle(['o', ])
    properties = plot_util.fill_with_defaults(properties)

    #markers = 'o'
    #colors = itertools.cycle(["#e41a1c",    # Red
    #                          "#377eb8",    # Blue
    #                          "#4daf4a",    # Green
    #                          "#984ea3",    # Purple
    #                          "#ff7f00",    # Orange
    #                          "#ffff33",    # Yellow
    #                          "#a65628",    # Brown
    #                          "#f781bf",    # Pink
    #                          "#999999"])   # Grey
    #linestyles = '-'

    size = 1
    # Set up figure
    ratio = 5
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=int(properties['dpi'])) #, figsize=(8, 4))
    ax1 = subplot(gs[0:ratio, :])
    ax1.grid(True, linestyle='-', which='major', color=properties["gridcolor"],
             alpha=float(properties["gridalpha"]))

    if title is not None:
        fig.suptitle(title, fontsize=int(properties["titlefontsize"]))

    auto_y_min = sys.maxint
    auto_y_max = -sys.maxint
    auto_x_min = sys.maxint

    for idx, performance in enumerate(performance_list):
        color = properties["colors"].next()
        marker = properties["markers"].next()
        linestyle = properties["linestyles"].next()
        name_list[idx] = name_list[idx].replace("_", " ")
        median = np.median(performance, axis=0)
        upper_quartile = np.percentile(performance, q=75, axis=0)
        lower_quartile = np.percentile(performance, q=25, axis=0)
        print("Final incumbent performance (% 20s): %s" % (name_list[idx], median[-1]))
        if logy:
            lower_quartile[lower_quartile < 0.0001] = 0.0001
            median[median < 0.0001] = 0.0001

        # Plot mean and std
        ax1.fill_between(times, lower_quartile, upper_quartile,
                         facecolor=color, alpha=0.3, edgecolor=color)
        ax1.plot(times, median, color=color,
                 linewidth=int(properties["linewidth"]), linestyle=linestyle,
                 marker=marker, markersize=int(properties["markersize"]),
                 label=name_list[idx],
                 )
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
    ax1.set_ylabel("%s" % ylabel, fontsize=properties["labelfontsize"])
    ax1.set_xlabel("time [sec]", fontsize=properties["labelfontsize"])

    leg = ax1.legend(loc='best', fancybox=True, prop={'size': int(properties["legendsize"])})
    leg.get_frame().set_alpha(0.5)



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

    tick_params(axis='both', which='major', labelsize=properties["ticklabelsize"])

    # Set axes limits
    if logx:
        ax1.set_xscale("log")
    if logy:
        ax1.set_yscale("log")

    return fig


def plot_optimization_trace_mult_exp(time_list, performance_list, name_list,
                                     title=None, logy=False, logx=False,
                                     properties=None, y_min=None,
                                     y_max=None, x_min=None, x_max=None,
                                     ylabel="Performance", scale_std=1,
                                     agglomeration="mean"):

    # complete properties
    if properties is None:
        properties = dict()
    properties = plot_util.fill_with_defaults(properties)

    size = 1
    # Set up figure
    ratio = 5
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=int(properties['dpi'])) #, figsize=(8, 4))
    ax1 = subplot(gs[0:ratio, :])
    ax1.grid(True, linestyle='-', which='major', color=properties["gridcolor"],
             alpha=float(properties["gridalpha"]))

    if title is not None:
        fig.suptitle(title, fontsize=int(properties["titlefontsize"]))

    auto_y_min = sys.maxint
    auto_y_max = -sys.maxint
    auto_x_min = sys.maxint
    auto_x_max = -sys.maxint

    for idx, performance in enumerate(performance_list):
        performance = np.array(performance)

        color = properties["colors"].next()
        marker = properties["markers"].next()
        linestyle = properties["linestyles"].next()
        name_list[idx] = name_list[idx].replace("_", " ")

        if logx and time_list[idx][0] == 0:
            time_list[idx][0] = 10**-1

        if agglomeration == "mean":
            m = np.mean(performance, axis=0)
            lower = m + np.std(performance, axis=0)*scale_std
            upper = m - np.std(performance, axis=0)*scale_std
        elif agglomeration == "median":
            m = np.median(performance, axis=0)
            lower = np.percentile(performance, axis=0, q=25)
            upper = np.percentile(performance, axis=0, q=75)
        else:
            raise ValueError("Unknown agglomeration: %s" % agglomeration)

        if logy:
            lower[lower < 0.0001] = 0.0001

        # Plot mean and std
        if scale_std >= 0 and len(performance) > 1:
            ax1.fill_between(time_list[idx], lower, upper, facecolor=color,
                             alpha=0.3, edgecolor=color)
        ax1.plot(time_list[idx], m, color=color,
                 linewidth=int(properties["linewidth"]), linestyle=linestyle,
                 marker=marker, markersize=int(properties["markersize"]),
                 label=name_list[idx],
                 )

        # Get limits
        # For y_min we always take the lowest value

        # find out show from for this time_list
        show_from = 0
        if x_min != None:
            for t_idx, t in enumerate(time_list[idx]):
                if t > x_min:
                    show_from = t_idx
                    break

        auto_y_min = min(min(lower[show_from:]), auto_y_min)
        auto_y_max = max(max(upper[show_from:]), auto_y_max)

        auto_x_min = min(time_list[idx][0], auto_x_min)
        auto_x_max = max(time_list[idx][-1], auto_x_max)

    # Describe axes
    if logy:
        ax1.set_yscale("log")
        auto_y_min = max(0.1, auto_y_min)
    ax1.set_ylabel("%s" % ylabel, fontsize=properties["labelfontsize"])

    if logx:
        ax1.set_xscale("log")
        auto_x_min = max(0.1, auto_x_min)
    ax1.set_xlabel("time [sec]", fontsize=properties["labelfontsize"])

    leg = ax1.legend(loc='best', fancybox=True, prop={'size': int(properties["legendsize"])})
    leg.get_frame().set_alpha(0.5)

    tick_params(axis='both', which='major', labelsize=properties["ticklabelsize"])

    # Set axes limits
    if y_max is None and y_min is not None:
        ax1.set_ylim([y_min, auto_y_max + 0.01*abs(auto_y_max - y_min)])
    elif y_max is not None and y_min is None:
        ax1.set_ylim([auto_y_min - 0.01*abs(auto_y_max - auto_y_min), y_max])
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

    return fig
