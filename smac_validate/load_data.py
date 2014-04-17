#!/usr/bin/env python

import csv
import os


def read_csv(fn, has_header=True, data_type=str):
    data = list()
    header = None
    with open(fn, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csv_reader:
            if header is None and has_header:
                header = row
                continue
            data.append(map(data_type, [i.strip() for i in row]))
    return header, data


def get_file_and_name_list(argument_list, match_file):
    """
    argument_list: [<whatisthis> <file>*]*
    match_file: string which only appears in file and not in whatisthis
    """
    name_list = list()
    file_list = list()
    no_data = False
    for i in range(len(argument_list)):
        if not match_file in argument_list[i] and no_data:
            raise ValueError("You need at least one %s file per Experiment, %s has none" % (match_file, name_list[-1]))
        elif not match_file in argument_list[i] and not no_data:
            name_list.append(argument_list[i])
            file_list.append(list())
            no_data = True
            continue
        else:
            if os.path.exists(argument_list[i]):
                no_data = False
                file_list[-1].append(os.path.abspath(argument_list[i]))
            else:
                raise ValueError("%s is not a valid file" % argument_list[i])
    if no_data:
        raise ValueError("You need at least one %s file per Experiment,  %s has none" % (match_file, name_list[-1]))
    return file_list, name_list