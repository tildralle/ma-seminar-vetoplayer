import numpy as np
from src.sprayer import Sprayer
sprayer = Sprayer()

def choose_cases(dataframe,column_name,cases):
    snippet = dataframe.loc[dataframe[column_name].isin(cases)]
    
    not_found = np.array([])
    for i in cases:
        if i not in np.array(dataframe[column_name]):
            not_found = np.append(not_found,i)
    not_found = np.sort(not_found)
    if len(not_found) == 0:
        print(sprayer.success('Every case found.'))
    else:
        print(sprayer.dye('Cases not found:', "WARNING"), not_found)
    return snippet

def find_columns_of_values(dataframe,*values):
    correct_columns = np.array([])
    columns = dataframe.columns
    for val in values:
        val_check = 0
        argument_array = np.array([])
        for c in columns:
            column = np.array(dataframe[c])
            if val in column:
                val_check += 1
                correct_columns = np.append(correct_columns,c)
                argument_array = np.append(argument_array, c)
            elif val_check > 1 and c == columns[-1]:
                print(f'Caution: Argument {val} found in several columns: ', argument_array)
            elif val_check == 0 and c == columns[-1]:
                print(f'Caution: Argument {val} not found in data')
            else:
                continue
    return correct_columns

def group_it(dataframe,arguments,columns,*column_names):
    if len(arguments) == 0:
        snippet = dataframe
    elif len(column_names) != 0:
        data_copy = dataframe.copy()
        for c, arg in zip(column_names,arguments):
            groups = data_copy.groupby(c)
            arg_type = type(arg)
            column_as_array = np.array(data_copy[c]).astype(arg_type).flatten()
            if arg in column_as_array:
                snippet = groups.get_group(arg)
                data_copy = snippet
            else:
                print(f'Caution: Argument {arg} not found in column {c}')
                snip = []
                return snip
    else:
        correct_columns = find_columns_of_values(dataframe,*arguments)
        if len(correct_columns) == 0:
            snip = []
            return snip
        data_copy = dataframe.copy()
        for c, arg in zip(correct_columns,arguments):
            groups = data_copy.groupby(c)
            snippet = groups.get_group(arg)
            data_copy = snippet

    if len(columns) == 0:
        snip = snippet
    else:
        snip = snippet.loc[:,[*columns]]

    return snip