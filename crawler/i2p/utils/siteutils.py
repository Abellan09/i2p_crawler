# -*- coding: utf-8 -*-


"""
    :mod:`siteutils`
    ===========================================================================
    :synopsis: site utilities
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

import os


def get_initial_seeds(path_to_file):
    """
    Gets a list of initial site seeds

    :param path_to_file: srt - Path to the *.txt file of gathered site seeds
    :return: new_list: list - Site seed list
    """

    # Gets all seeds from the file
    with open(path_to_file) as seeds:
        list_seeds = seeds.readlines()

    # New list
    new_list = []

    # Postprocessing the list
    for seed in list_seeds:
        seed = str.replace(seed, '\n', '')
        seed = str.replace(seed, '\r', '')
        new_list.append(seed)

    return new_list


def tail(path_to_file, n=1):
    """
    Executes tail on unix based systems

    :param path_to_file: str - Path to the file
    :param n: int - Number of lines
    :return: lines_str: str - Last n lines concatenated
    """

    lines_str = os.popen('tail -n ' + str(n) + ' ' + path_to_file).read()
    return lines_str
