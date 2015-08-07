import itertools
import sys

from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, savefig, show
import matplotlib.gridspec
import numpy as np

import plot_util


def plot_optimization_trace(times, performance_list, title, name_list,
                            log=False, save="", y_min=None, y_max=None,
                            x_min=None, x_max=None):
    '''
    plots a median optimization trace based one time array
    '''
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


def plot_optimization_trace_mult_exp(time_list, performance_list, name_list,
                                     title=None, logy=False, logx=False,
                                     save="", properties=None, y_min=None,
                                     y_max=None, x_min=None, x_max=None,
                                     ylabel="Performance", scale_std=1,
                                     agglomeration="mean"):
    # complete properties
    if properties is None:
        properties = dict()
    properties['markers'] = itertools.cycle(['o', 's', '^', '*'])
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
        color = properties["colors"].next()
        marker = properties["markers"].next()
        linestyle = properties["linestyles"].next()
        name_list[idx] = name_list[idx].replace("_", " ")

        if logy:
            performance = np.log10(performance)
        if logx and time_list[idx][0] == 0:
            time_list[idx][0] = 10**-1
        if agglomeration == "mean":
            mean = np.mean(performance, axis=0)
            std_lo = np.std(performance, axis=0)*scale_std
            std_up = std_lo
        elif agglomeration == "median":
            mean = np.median(performance, axis=0)
            std_lo = np.percentile(performance, q=75, axis=0)*scale_std
            std_up = np.percentile(performance, q=25, axis=0)*scale_std
        else:
            raise ValueError("'agglomeration' is not in ('mean', 'median')")

        # Plot mean and std
        if scale_std >= 0 and len(performance) > 1:
            ax1.fill_between(time_list[idx], mean-std_lo, mean+std_up,
                             facecolor=color, alpha=0.3, edgecolor=color)
        ax1.plot(time_list[idx], mean, color=color,
                 linewidth=int(properties["linewidth"]), linestyle=linestyle,
                 marker=marker, markersize=int(properties["markersize"]),
                 label=name_list[idx],
                 )

        # Get limits
        # For y_min we always take the lowest value
        auto_y_min = min(min(mean[x_min:]-std_lo[x_min:]), auto_y_min)
        auto_y_max = max(max(mean[x_min:]+std_up[x_min:]), auto_y_max)

        auto_x_min = min(time_list[idx][0], auto_x_min)
        auto_x_max = max(time_list[idx][-1], auto_x_max)

    # Describe axes
    if logy:
        ax1.set_ylabel("log10(%s)" % ylabel, fontsize=properties["labelfontsize"])
    else:
        ax1.set_ylabel("%s" % ylabel, fontsize=properties["labelfontsize"])

    if logx:
        ax1.set_xlabel("log10(time) [sec]", fontsize=properties["labelfontsize"])
        ax1.set_xscale("log")
        auto_x_min = max(0.1, auto_x_min)
    else:
        ax1.set_xlabel("time [sec]")

    leg = ax1.legend(loc='best', fancybox=True, prop={'size': int(properties["legendsize"])})
    leg.get_frame().set_alpha(0.5)

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

    # Save or show
    tight_layout()
    #subplots_adjust(top=0.85)
    if save != "":
        print "Save plot to %s" % save
        savefig(save, dpi=int(properties['dpi']), facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.1)
    else:
        show()