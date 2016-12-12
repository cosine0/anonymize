"""
public functions
"""

# !/usr/bin/env python
# coding=utf-8


def cmp_str(element1, element2):
    """
    compare number in str format correctley
    """
    try:
        return cmp(int(element1), int(element2))
    except ValueError:
        return cmp(element1, element2)


def list_to_str(value_list, compare_function_of_sort=cmp, sep=';'):
    """covert sorted str list (sorted by compare_function_of_sort) to str
    value (splited by sep). This fuction is value safe, which means
    value_list will not be changed.
    return str list.
    """
    temp = sorted(value_list[:], cmp=compare_function_of_sort)
    return sep.join(temp)
