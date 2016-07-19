#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import numpy as np
import tabulate

from plottingscripts.utils import read_util, plot_util
import plottingscripts.plotting.plot_methods as plot_methods

def main():
    prog = "python get_percentage_solved.py <WhatIsThis> one/or/many/*RunResultLineMatrix-traj*.csv"
    description = "Returns a table with average percentage of solved instances"

    parser = ArgumentParser(description=description, prog=prog)

    # General Options
    parser.add_argument("-s", "--save", dest="save",
                        default="", help="Where to save tex table instead of showing it?")
    parser.add_argument("-t", "--title", dest="title",
                        default="", help="Optional supertitle for plot")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
                        help="print number of runs on plot")
    args, unknown = parser.parse_known_args()

    # Get files and names
    file_list, name_list = read_util.get_file_and_name_list(unknown, match_file='.csv')
    for idx in range(len(name_list)):
        print "%20s contains %d file(s)" % (name_list[idx], len(file_list[idx]))

    if args.verbose:
        name_list = [name_list[i] + " (" + str(len(file_list[i])) + ")" for i in range(len(name_list))]

    # Get data from csv
    solutions = dict()
    allowed_solutions = ("SAT", "UNSAT", "TIMEOUT", "CRASHED", "KILLED")
    num_instances = None
    for name in range(len(name_list)):
        print "Read %s" % name_list[name]
        # We have a new experiment
        solutions[name_list[name]] = dict()
        for s in allowed_solutions:
            solutions[name_list[name]][s] = 0
        solutions[name_list[name]]["runs"] = 0

        for fl in file_list[name]:
            solutions[name_list[name]]["runs"] += 1
            _none, csv_data = read_util.read_csv(fl, has_header=True)
            if num_instances is None:
                num_instances = len(csv_data)
            else:
                assert num_instances == len(csv_data), \
                    "Found a different number of instances (%s): %f != %f" % \
                    (fl, num_instances, len(csv_data))
            # get last configuration
            for instance in range(num_instances):
                # -5 is the solution for the final incumbent
                # if there is no additional info
                sol = csv_data[instance][-5].replace('"', '').strip()
                try:
                    solutions[name_list[name]][sol] += 1
                except KeyError:
                    # -6 is the solution for the final incumbent
                    # if there is additional info
                    sol = csv_data[instance][-6].replace('"', '').strip()
                    solutions[name_list[name]][sol] += 1

    # Reorganize dictionary
    tab_dict = list()
    tab_dict.append(["", ])
    for key in sorted(solutions.keys()):
        tab_dict[0].append(key)

    # num runs
    tab_dict.append(["num_runs"])
    for key in sorted(solutions.keys()):
        tab_dict[-1].append(solutions[key]["runs"])

    # Mean of solutions
    for sol in sorted(allowed_solutions):
        ls = list([sol, ])
        for key in sorted(solutions.keys()):
            ls.append(round(solutions[key][sol] / float(solutions[key]["runs"]), 2))
        tab_dict.append(ls)

    # calc %solved
    tab_dict.append(["%SOLVED"])
    for key in sorted(solutions.keys()):
        per_solved = (solutions[key]["SAT"]+solutions[key]["UNSAT"])/float((np.sum([solutions[key][i] for i in allowed_solutions])))
        tab_dict[-1].append(round(per_solved, 4)*100)

    print tabulate.tabulate(tab_dict, )

if __name__ == "__main__":
    main()