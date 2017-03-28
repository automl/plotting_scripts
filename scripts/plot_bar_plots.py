#!/usr/bin/env python
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys
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
    algorithms = set()
    for idx in range(len(name_list)):
        datasets.add(name_list[idx][0])
        algorithms.add(name_list[idx][1])
        assert len(file_list[idx]) == 1, "%s" % file_list[idx]
        print("%20s contains %d file(s)" %
              (name_list[idx], len(file_list[idx])))




if __name__ == "__main__":
    main()