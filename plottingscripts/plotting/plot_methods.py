from matplotlib.pyplot import tight_layout, figure, subplots_adjust, subplot, \
    savefig, show, tick_params
import matplotlib.gridspec
import numpy as np

import plottingscripts.utils.plot_util as plot_util
import plottingscripts.utils.macros


def plot_optimization_trace_mult_exp(time_list, performance_list, name_list,
                                     title=None, logy=False, logx=False,
                                     properties=None, y_min=None,
                                     y_max=None, x_min=None, x_max=None,
                                     ylabel="Performance", xlabel="time [sec]",
                                     scale_std=1, agglomeration="mean"):

    if scale_std != 1 and agglomeration == "median":
        raise ValueError("Can not scale_std when plotting median")

    # complete properties
    if properties is None:
        properties = dict()
    properties = plot_util.fill_with_defaults(properties)

    # Set up figure
    ratio = 5
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=int(properties['dpi']))
    ax1 = subplot(gs[0:ratio, :])
    ax1.grid(True, linestyle='-', which='major', color=properties["gridcolor"],
             alpha=float(properties["gridalpha"]))

    if title is not None:
        fig.suptitle(title, fontsize=int(properties["titlefontsize"]))

    auto_y_min = 2**64
    auto_y_max = -plottingscripts.utils.macros.MAXINT
    auto_x_min = 2**64
    auto_x_max = -2**64

    for idx, performance in enumerate(performance_list):
        performance = np.array(performance)

        color = next(properties["colors"])
        marker = next(properties["markers"])
        linestyle = next(properties["linestyles"])
        name_list[idx] = name_list[idx].replace("_", " ")

        if logx and time_list[idx][0] == 0:
            time_list[idx][0] = 10**-1

        print("Plot %s" % agglomeration)
        if agglomeration == "mean":
            m = np.mean(performance, axis=0)
            lower = m - np.std(performance, axis=0)*scale_std
            upper = m + np.std(performance, axis=0)*scale_std
        elif agglomeration == "median":
            m = np.median(performance, axis=0)
            lower = np.percentile(performance, axis=0, q=25)
            upper = np.percentile(performance, axis=0, q=75)
        else:
            raise ValueError("Unknown agglomeration: %s" % agglomeration)

        if logy:
            lower[lower < 0.0001] = 0.0001

        # Plot m and fill between lower and upper
        if scale_std >= 0 and len(performance) > 1:
            ax1.fill_between(time_list[idx], lower, upper, facecolor=color,
                             alpha=0.3, edgecolor=color)
        ax1.plot(time_list[idx], m, color=color,
                 linewidth=int(properties["linewidth"]), linestyle=linestyle,
                 marker=marker, markersize=int(properties["markersize"]),
                 label=name_list[idx])

        # find out show from for this time_list
        show_from = 0
        if x_min is not None:
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
    ax1.set_xlabel(xlabel, fontsize=properties["labelfontsize"])

    leg = ax1.legend(loc='best', fancybox=True,
                     prop={'size': int(properties["legendsize"])})
    leg.get_frame().set_alpha(0.5)

    tick_params(axis='both', which='major',
                labelsize=properties["ticklabelsize"])

    # Set axes limits
    if y_max is None and y_min is not None:
        ax1.set_ylim([y_min, auto_y_max + 0.01*abs(auto_y_max - y_min)])
    elif y_max is not None and y_min is None:
        ax1.set_ylim([auto_y_min - 0.01*abs(auto_y_max - auto_y_min), y_max])
    elif y_max is not None and y_min is not None and y_max > y_min:
        ax1.set_ylim([y_min, y_max])
    else:
        ax1.set_ylim([auto_y_min - 0.01*abs(auto_y_max - auto_y_min),
                      auto_y_max + 0.01*abs(auto_y_max - auto_y_min)])

    if x_max is None and x_min is not None:
        ax1.set_xlim([x_min - 0.1*abs(x_min), auto_x_max + 0.1*abs(auto_x_max)])
    elif x_max is not None and x_min is None:
        ax1.set_xlim([auto_x_min - 0.1*abs(auto_x_min), x_max + 0.1*abs(x_max)])
    elif x_max is not None and x_min is not None and x_max > x_min:
        ax1.set_xlim([x_min, x_max])
    else:
        ax1.set_xlim([auto_x_min,
                      auto_x_max + 0.1*abs(auto_x_min - auto_x_max)])

    return fig
