import itertools


def get_empty_iterator():
    return itertools.cycle([None])


def get_plot_markers():
    return itertools.cycle(['o'])
    #return itertools.cycle(['o', 's', 'x', '^', 'p', 'v', '>', '<', '8', '*',
    #                        '+', 'D'])


def get_plot_linestyles():
    return itertools.cycle(['-', '--', '-.', ':', ])


def get_single_linestyle():
    return itertools.cycle(['-'])


def get_plot_colors():
    # color brewer, 2nd qualitative 9 color scheme (http://colorbrewer2.org/)
    return itertools.cycle([#"#000000",    # Black
                            "#e41a1c",    # Red
                            "#377eb8",    # Blue
                            "#4daf4a",    # Green
                            "#984ea3",    # Purple
                            "#ff7f00",    # Orange
                            "#ffff33",    # Yellow
                            "#a65628",    # Brown
                            "#f781bf",    # Pink
                            "#999999",    # Grey
                            ])


def get_defaults():
    default = {"linestyles": get_single_linestyle(),
               "colors": get_plot_colors(),
               "markers": get_plot_markers(),
               "markersize": 10,
               "labelfontsize": 12,
               "linewidth": 1,
               "titlefontsize": 15,
               "gridcolor": 'lightgrey',
               "gridalpha": 0.5,
               "dpi": 100,
               "legendsize": 12,
               "legendlocation": "best",
               "ticklabelsize": 12,
               "drawstyle": "default",
               "incheswidth": 8.0,
               "inchesheight": 6.0,
               "loweryloglimit": 10e-10
               }
    return default


def fill_with_defaults(def_dict):
    defaults = get_defaults()
    for key in defaults:
        if key not in def_dict:
            def_dict[key] = defaults[key]
        elif def_dict[key] is None:
            def_dict[key] = defaults[key]
        else:
            pass
    return def_dict


def save_plot(fig, save, dpi):
    fig.tight_layout()
    fig.savefig(save, dpi=dpi, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.02, bbox_inches='tight')