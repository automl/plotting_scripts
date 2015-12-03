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
        if not match_file in argument_list[i] and len_desc == len_name:
            # We have all names, but next argument is not a file
            raise ValueError("You need at least one %s file per Experiment, %s has none" % (match_file, name_list[-1]))
        elif not match_file in argument_list[i] and len_desc < len_name:
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