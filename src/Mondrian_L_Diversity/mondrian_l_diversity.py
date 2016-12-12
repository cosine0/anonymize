"""
main module of mondrian_l_diversity
"""
# !/usr/bin/env python
# coding=utf-8

# @InProceedings{LeFevre2006a,
#   Title = {Workload-aware Anonymization},
#   Author = {LeFevre, Kristen and DeWitt, David J. and Ramakrishnan, Raghu},
#   Booktitle = {Proceedings of the 12th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
#   Year = {2006},
#   Address = {New York, NY, USA},
#   Pages = {277--286},
#   Publisher = {ACM},
#   Series = {KDD '06},
#   Acmid = {1150435},
#   Doi = {10.1145/1150402.1150435},
#   ISBN = {1-59593-339-5},
#   Keywords = {anonymity, data recoding, predictive modeling, privacy},
#   Location = {Philadelphia, PA, USA},
#   Numpages = {10},
#   Url  = {http://doi.acm.org/10.1145/1150402.1150435}
# }

# 2014-10-12

import pdb
import time
from models.numrange import NumRange
from models.gentree import GenTree
from utils.utility import list_to_str, cmp_str

__DEBUG = False
NUMBER_OF_QUASI_IDENTIFIER = 10
GLOBAL_L_VALUE = 5
RESULT = []
ATTRIBUTE_TREES = []
QUASI_IDENTIFIER_RANGE = []
IS_CATEGORICAL = []


class Partition(object):
    """Class for Group, which is used to keep records
    Store tree node in instances.
    self.member: records in group
    self.width: width of this partition on each domain
    self.middle: save the generalization result of this partition
    self.allow: 0 donate that not allow to split, 1 donate can be split
    """

    def __init__(self, data, width, middle):
        """
        initialize with data, width and middle
        """
        self.member = data[:]
        self.width = list(width)
        self.middle = list(middle)
        self.allow = [1] * NUMBER_OF_QUASI_IDENTIFIER

    def add_record(self, record):
        """
        add record to partition
        """
        self.member.append(record)

    def __len__(self):
        """
        return the number of records in partition
        """
        return len(self.member)


def check_diversity(data):
    """
    check the distinct SA values in dataset
    """
    sensitive_attribute_dict = {}
    for record in data:
        try:
            sensitive_attribute_value = list_to_str(record[-1])
        except AttributeError:
            sensitive_attribute_value = record[-1]
        try:
            sensitive_attribute_dict[sensitive_attribute_value] += 1
        except KeyError:
            sensitive_attribute_dict[sensitive_attribute_value] = 1
    return len(sensitive_attribute_dict)


def check_L_diversity(partition):
    """check if partition satisfy l-diversity
    return True if satisfy, False if not.
    """
    sensitive_attribute_dict = {}
    if len(partition) < GLOBAL_L_VALUE:
        return False
    if isinstance(partition, Partition):
        records_set = partition.member
    else:
        records_set = partition
    number_of_records = len(records_set)
    for record in records_set:
        try:
            sensitive_attribute_value = list_to_str(record[-1])
        except AttributeError:
            sensitive_attribute_value = record[-1]
        try:
            sensitive_attribute_dict[sensitive_attribute_value] += 1
        except KeyError:
            sensitive_attribute_dict[sensitive_attribute_value] = 1
    if len(sensitive_attribute_dict.keys()) < GLOBAL_L_VALUE:
        return False
    if len(sensitive_attribute_dict) >= GLOBAL_L_VALUE:
        return True
    return False


def get_normalized_width(partition, index):
    """
    return Normalized width of partition
    similar to NCP
    """
    if IS_CATEGORICAL[index] is False:
        low = partition.width[index][0]
        high = partition.width[index][1]
        width = float(ATTRIBUTE_TREES[index].sort_value[high]) - float(ATTRIBUTE_TREES[index].sort_value[low])
    else:
        width = partition.width[index]
    return width * 1.0 / QUASI_IDENTIFIER_RANGE[index]


def choose_dimension(partition):
    """choose dimension with largest normalized Width
    return dimension index.
    """
    max_witdh = -1
    max_dim = -1
    for i in range(NUMBER_OF_QUASI_IDENTIFIER):
        if partition.allow[i] == 0:
            continue
        norm_width = get_normalized_width(partition, i)
        if norm_width > max_witdh:
            max_witdh = norm_width
            max_dim = i
    if max_witdh > 1:
        print "Error: max_witdh > 1"
        pdb.set_trace()
    if max_dim == -1:
        print "cannot find the max dim"
        pdb.set_trace()
    return max_dim


def frequency_set(partition, dim):
    """get the frequency_set of partition on dim
    return dict{key: str values, values: count}
    """
    frequency = {}
    for record in partition.member:
        try:
            frequency[record[dim]] += 1
        except KeyError:
            frequency[record[dim]] = 1
    return frequency


def find_median(partition, dim):
    """find the middle of the partition
    return split_val
    """
    frequency = frequency_set(partition, dim)
    split_val = ''
    next_val = ''
    value_list = frequency.keys()
    value_list.sort(cmp=cmp_str)
    total = sum(frequency.values())
    middle = total / 2
    if middle < GLOBAL_L_VALUE:
        return '', '', '', ''
    index = 0
    split_index = 0
    for i, qid_value in enumerate(value_list):
        index += frequency[qid_value]
        if index >= middle:
            split_val = qid_value
            split_index = i
            break
    else:
        print "Error: cannot find split_val"
    try:
        next_val = value_list[split_index + 1]
    except IndexError:
        next_val = split_val
    return split_val, next_val, value_list[0], value_list[-1]


def split_numeric_value(numeric_value, splitVal, nextVal):
    """
    split numeric value on splitVal
    return sub ranges
    """
    split_result = numeric_value.split(',')
    if len(split_result) <= 1:
        return split_result[0], split_result[0]
    else:
        low = split_result[0]
        high = split_result[1]
        # Fix 2,2 problem
        if low == splitVal:
            lvalue = low
        else:
            lvalue = low + ',' + splitVal
        if high == splitVal:
            rvalue = high
        else:
            rvalue = nextVal + ',' + high
        return lvalue, rvalue


def anonymize(partition):
    """
    Main procedure of mondrian_l_diversity.
    recursively partition groups until not allowable.
    """
    allow_count = sum(partition.allow)
    for index in range(allow_count):
        dimension = choose_dimension(partition)
        if dimension == -1:
            print "Error: dimension=-1"
            pdb.set_trace()
        pwidth = partition.width
        pmiddle = partition.middle
        if IS_CATEGORICAL[dimension] is False:
            # numeric attributes
            splitVal, nextVal, low, high = find_median(partition, dimension)
            # update low and high
            if low is not '':
                partition.low[dimension] = QI_DICT[dimension][low]
                partition.high[dimension] = QI_DICT[dimension][high]
            if splitVal == '':
                partition.allow[dimension] = 0
                continue
            middle_pos = ATTRIBUTE_TREES[dimension].dict[splitVal]
            lhs_middle = pmiddle[:]
            rhs_middle = pmiddle[:]
            lhs_middle[dimension], rhs_middle[dimension] = split_numeric_value(pmiddle[dimension], splitVal, nextVal)
            lhs_width = pwidth[:]
            rhs_width = pwidth[:]
            lhs_width[dimension] = (pwidth[dimension][0], middle_pos)
            rhs_width[dimension] = (ATTRIBUTE_TREES[dimension].dict[nextVal], pwidth[dimension][1])
            lhs = []
            rhs = []
            for record in partition.member:
                pos = ATTRIBUTE_TREES[dimension].dict[record[dimension]]
                if pos <= middle_pos:
                    # lhs = [low, means]
                    lhs.append(record)
                else:
                    # rhs = (means, high]
                    rhs.append(record)
            if check_L_diversity(lhs) is False or check_L_diversity(rhs) is False:
                partition.allow[dimension] = 0
                continue
            # anonymize sub-partition
            anonymize(Partition(lhs, lhs_width, lhs_middle))
            anonymize(Partition(rhs, rhs_width, rhs_middle))
            return
        else:
            # normal attributes
            split_node = ATTRIBUTE_TREES[dimension][partition.middle[dimension]]
            if len(split_node.child) == 0:
                partition.allow[dimension] = 0
                continue
            sub_node = [t for t in split_node.child]
            sub_partitions = []
            for i in range(len(sub_node)):
                sub_partitions.append([])
            for record in partition.member:
                quasi_identifier_value = record[dimension]
                for i, node in enumerate(sub_node):
                    if quasi_identifier_value in node.cover:
                        sub_partitions[i].append(record)
                        break
                else:
                    print "Generalization hierarchy error!"
                    pdb.set_trace()

            l_satisfied = True
            for sub_partition in sub_partitions:
                if len(sub_partition) == 0:
                    continue
                if not check_L_diversity(sub_partition):
                    l_satisfied = False
                    break
            if l_satisfied:
                for i, sub_partition in enumerate(sub_partitions):
                    if len(sub_partition) == 0:
                        continue
                    wtemp = pwidth[:]
                    mtemp = pmiddle[:]
                    wtemp[dimension] = len(sub_node[i])
                    mtemp[dimension] = sub_node[i].value
                    anonymize(Partition(sub_partition, wtemp, mtemp))
                return
            else:
                partition.allow[dimension] = 0
                continue
    RESULT.append(partition)


def init(attribute_trees, data, l_value, number_of_quasi_identifier=None):
    """
    resset global variables
    """
    global GLOBAL_L_VALUE, RESULT, NUMBER_OF_QUASI_IDENTIFIER, ATTRIBUTE_TREES, QUASI_IDENTIFIER_RANGE, IS_CATEGORICAL
    ATTRIBUTE_TREES = attribute_trees
    if number_of_quasi_identifier is None:
        NUMBER_OF_QUASI_IDENTIFIER = len(data[0]) - 1
    else:
        NUMBER_OF_QUASI_IDENTIFIER = number_of_quasi_identifier
    for generalization_tree in attribute_trees:
        if isinstance(generalization_tree, NumRange):
            IS_CATEGORICAL.append(False)
        else:
            IS_CATEGORICAL.append(True)
    GLOBAL_L_VALUE = l_value
    RESULT = []
    QUASI_IDENTIFIER_RANGE = []


def mondrian_l_diversity(attribute_trees, data, l_value, nubmer_of_quasy_idnetifier=None):
    """
    Mondrian for l-diversity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    init(attribute_trees, data, l_value, nubmer_of_quasy_idnetifier)
    middle = []
    result = []
    whole_qi_attributes = []
    for i in range(NUMBER_OF_QUASI_IDENTIFIER):
        if IS_CATEGORICAL[i] is False:
            QUASI_IDENTIFIER_RANGE.append(ATTRIBUTE_TREES[i].range)
            whole_qi_attributes.append((0, len(ATTRIBUTE_TREES[i].sort_value) - 1))
            middle.append(ATTRIBUTE_TREES[i].value)
        else:
            QUASI_IDENTIFIER_RANGE.append(len(ATTRIBUTE_TREES[i]['*']))
            whole_qi_attributes.append(len(ATTRIBUTE_TREES[i]['*']))
            middle.append('*')
    whole_partition = Partition(data, whole_qi_attributes, middle)
    start_time = time.time()
    anonymize(whole_partition)
    rtime = float(time.time() - start_time)
    ncp = 0.0
    dp = 0.0
    for partition in RESULT:
        rncp = 0.0
        dp += len(partition) ** 2
        for index in range(NUMBER_OF_QUASI_IDENTIFIER):
            rncp += get_normalized_width(partition, index)
        for index in range(len(partition)):
            gen_result = partition.middle + [partition.member[index][-1]]
            result.append(gen_result[:])
        rncp *= len(partition)
        ncp += rncp
    ncp /= NUMBER_OF_QUASI_IDENTIFIER
    ncp /= len(data)
    ncp *= 100
    if __DEBUG:
        print "L=%d" % l_value
        from decimal import Decimal
        print "Discernability Penalty=%.2E" % Decimal(str(dp))
        print "Diversity", check_diversity(data)
        # If the number of raw data is not eual to number published data
        # there must be some problems.
        print "size of partitions", len(RESULT)
        print "Number of Raw Data", len(data)
        print "Number of Published Data", sum([len(t) for t in RESULT])
        # print [len(t) for t in RESULT]
        print "NCP = %.2f %%" % ncp
    if len(result) != len(data):
        print "Error: lose records"
        pdb.set_trace()
    return result, (ncp, rtime)
