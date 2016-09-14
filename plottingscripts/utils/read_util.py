import csv
import os


def read_csv(fn, has_header=True, data_type=str):
    data = list()
    header = None
    with open(fn, 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csv_reader:
            if header is None and has_header:
                header = row
                continue
            data.append(list(map(data_type, [i.strip() for i in row])))
    return header, data


def get_file_and_name_list(argument_list, match_file, len_name=1):
    """
    argument_list: [<whatisthis> <file>*]*
    match_file: string which only appears in file and not in whatisthis
    len_name: len of names describing file(s) (if >1 return list of tuples)
    """
    assert 0 < len_name == int(len_name)
    name_list = list()
    file_list = list()
    len_desc = 0
    for i in range(len(argument_list)):
        if match_file not in argument_list[i] and len_desc == len_name:
            # We have all names, but next argument is not a file
            raise ValueError("You need at least one %s file per Experiment, "
                             "%s has none" % (match_file, name_list[-1]))
        elif match_file not in argument_list[i] and len_desc < len_name:
            # We start with a new name desc
            if len_name > 1 and len_desc == 0:
                name_list.append(list([argument_list[i], ]))
            elif len_name > 1 and len_desc > 0:
                name_list[-1].append(argument_list[i])
            else:
                name_list.append(argument_list[i])

            len_desc += 1

            if len_desc == len_name:
                # We have all desc for this file
                file_list.append(list())
            continue
        else:
            if os.path.exists(argument_list[i]):
                len_desc = 0
                file_list[-1].append(os.path.abspath(argument_list[i]))
            else:
                raise ValueError("%s is not a valid file" % argument_list[i])

    return file_list, name_list


def read_trajectory_file(fn):
    """ COPIED FROM pySMAC, modified to work on validate over time file
    Reads a trajectory file and returns a list of dicts with all the
    information.

    All values, like "Estimated Training Performance" and so on
    are floats.

    :param fn: name of file to read
    :type fn: str

    :returns: list of dicts -- every dict contains the keys:
        "CPU Time Used", "Estimated Training Performance",
        "Wallclock Time", "Incumbent ID","Automatic Configurator (CPU) Time", ..
    """
    return_list = []

    with open(fn, 'r') as fh:
        header = list(map(lambda s: s.strip('"'), fh.readline().split(",")))
        l_info = len(header)-1
        for line in fh.readlines():
            tmp = line.split(",")
            tmp_dict = {}
            for i in range(l_info):
                tmp_dict[header[i]] = float(tmp[i].strip().replace('"', ''))
            return_list.append(tmp_dict)
    return return_list


def read_validationObjectiveMatrix_file(fn):
    """ COPIED FROM pySMAC, modified to not use regexps
    reads the run data of a validation run performed by SMAC.

    For cases with instances, not necessarily every instance is used during the
    configuration phase to estimate a configuration's performance. If validation
    is enabled, SMAC reruns parameter settings (usually just the final
    incumbent) on the whole instance set/a designated test set. The data from
    those runs is stored in separate files. This function reads one of these
    files.

    :param fn: the name of the validationObjectiveMatrix file
    :type fn: str

    :returns: dict -- instances as keys, list of performances for each config
                      as list

    .. todo::
       testing of validation runs where more than the final incumbent is
       validated
    """
    values = {}

    with open(fn, 'r') as fh:
        header = fh.readline().split(",")
        num_configs = len(header) - 2
        for line in fh.readlines():
            line = line.split(",")
            inst = line[0].strip().replace('"', '').replace("'", "")
            if inst in values:
                raise ValueError("Cannot handle more than one "
                                 "seed per instance")
            values[inst] = [float(i.strip().replace('"', '').replace("'", ""))
                            for i in line[2:]]
            assert len(values[inst]) == num_configs

    return values
