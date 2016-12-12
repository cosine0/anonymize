"""
read adult data
"""

#!/usr/bin/env python
# coding=utf-8

# Read data and read tree fuctions for INFORMS data
# attributes ['age', 'workcalss', 'final_weight', 'education', 'education_num', 'matrital_status', 'occupation',
# 'relationship', 'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week', 'native_country', 'class']
# QID ['age', 'workcalss', 'education', 'matrital_status', 'race', 'sex', 'native_country']
# SA ['occopation']
from models.gentree import GenTree
from models.numrange import NumRange
from utils.utility import cmp_str
import pickle

import pdb

ATT_NAMES = ['age', 'workclass', 'final_weight', 'education',
             'education_num', 'marital_status', 'occupation', 'relationship',
             'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
             'native_country', 'class']
# 8 attributes are chose as QI attributes
# age and education levels are treated as numeric attributes
# only matrial_status and workclass has well defined generalization hierarchies.
# other categorical attributes only have 2-level generalization hierarchies.
# QI_INDEX = [0, 1, 4, 5, 8, 9, 13]
# IS_CATEGORICAL = [False, True, False, True, True, True, True]
QI_INDEX = [1, 5, 8, 9, 13]
IS_CATEGORICAL = [True, True, True, True, True]
# OCC as SA, do not use class wiht only has two values
SA_INDEX = 6

__DEBUG = False


def read_data():
    """
    read microda for *.txt and return read data
    """
    QI_num = len(QI_INDEX)
    data = []
    numeric_dicts = []
    for i in range(QI_num):
        numeric_dicts += [{}]
    # oder categorical attributes in intuitive order
    # here, we use the appear number
    data_file = open('data/adult.data', 'rU')
    for line in data_file:
        line = line.strip()
        # remove empty and incomplete lines
        # only 30162 records will be kept
        if len(line) == 0 or '?' in line:
            continue
        # remove double spaces
        line = line.replace(' ', '')
        columns = line.split(',')
        qi_columns = []
        for i in range(QI_num):
            index = QI_INDEX[i]
            if IS_CATEGORICAL[i] is False:
                try:
                    numeric_dicts[i][columns[index]] += 1
                except:
                    numeric_dicts[i][columns[index]] = 1
            qi_columns.append(columns[index])
        qi_columns.append(columns[SA_INDEX])
        data.append(qi_columns)
    # pickle numeric attributes and get NumRange
    for i in range(QI_num):
        if IS_CATEGORICAL[i] is False:
            static_file = open('data/adult_' + ATT_NAMES[QI_INDEX[i]] + '_static.pickle', 'wb')
            sort_value = list(numeric_dicts[i].keys())
            sort_value.sort(cmp=cmp_str)
            pickle.dump((numeric_dicts[i], sort_value), static_file)
            static_file.close()
    return data


def read_tree():
    """read tree from data/tree_*.txt, store them in att_tree
    """
    att_names = []
    att_trees = []
    for t in QI_INDEX:
        att_names.append(ATT_NAMES[t])
    for i in range(len(att_names)):
        if IS_CATEGORICAL[i]:
            att_trees.append(read_tree_file(att_names[i]))
        else:
            att_trees.append(read_pickle_file(att_names[i]))
    return att_trees


def read_pickle_file(att_name):
    """
    read pickle file for numeric attributes
    return numrange object
    """
    try:
        static_file = open('data/adult_' + att_name + '_static.pickle', 'rb')
        (numeric_dict, sort_value) = pickle.load(static_file)
    except:
        print "Pickle file not exists!!"
    static_file.close()
    result = NumRange(sort_value, numeric_dict)
    return result


def read_tree_file(tree_name):
    """read tree data from tree_name
    """
    leaf_to_path = {}
    att_tree = {}
    prefix = 'data/adult_'
    postfix = ".txt"
    tree_file = open(prefix + tree_name + postfix, 'rU')
    att_tree['*'] = GenTree('*')
    if __DEBUG:
        print "Reading Tree" + tree_name
    for line in tree_file:
        # delete \n
        if len(line) <= 1:
            break
        line = line.strip()
        levels = line.split(';')
        # copy levels
        levels.reverse()
        for level, level_value in enumerate(levels):
            is_leaf = False
            if level == len(levels) - 1:
                is_leaf = True
            # try and except is more efficient than 'in'
            if level_value not in att_tree:
                att_tree[level_value] = GenTree(level_value, att_tree[levels[level - 1]], is_leaf)
    if __DEBUG:
        print "Nodes No. = %d" % att_tree['*'].support
    tree_file.close()
    return att_tree
