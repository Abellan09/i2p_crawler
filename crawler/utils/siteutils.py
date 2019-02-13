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

from pony.orm import db_session

from database import dbutils,dbsettings

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

def get_crawling_status():
    """
    Gets a snapshot of how the crawling procedure is going

    :return: status: dict - The current crawling status
    """

    status = {}

    with db_session:
        status[dbsettings.Status.PENDING.name] = dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.PENDING)
        status[dbsettings.Status.ONGOING.name] = dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.ONGOING)
        status[dbsettings.Status.ERROR.name] = dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.ERROR)
        status[dbsettings.Status.DISCARDED.name] = dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.DISCARDED)
        status[dbsettings.Status.FINISHED.name] = dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.FINISHED)

    return status
