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

from database import dbutils, dbsettings

import os
import logging
import uuid


def get_seeds_from_file(path_to_file):
    """
    Gets a list of initial site seeds

    :param path_to_file: srt - Path to the *.txt file of gathered site seeds
    :return: new_list: list - Site seed list
    """

    # New list
    new_list = []

    try:
        # Gets all seeds from the file
        with open(path_to_file) as seeds:
            list_seeds = seeds.readlines()

        # Postprocessing the list
        for seed in list_seeds:
            seed = str.replace(seed, '\n', '')
            seed = str.replace(seed, '\r', '')
            new_list.append(seed)

    except Exception as e:
        logging.debug("ERROR getting seeds: %s", e)

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


def get_crawling_status(uuid):
    """
    Gets a snapshot of how the crawling procedure is going

    :param uuid: str - Crawling process UUID
    :return: status: dict - The current crawling status
    """

    status = {}

    with db_session:
        status[dbsettings.Status.PENDING.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.PENDING, uuid=uuid, sorting_desc=True)
        status[dbsettings.Status.ONGOING.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.ONGOING, uuid=uuid, sorting_desc=True)
        status[dbsettings.Status.ERROR.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.ERROR, uuid=uuid, sorting_desc=True)
        status[dbsettings.Status.ERROR_DEFUNC.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.ERROR_DEFUNC, uuid=uuid, sorting_desc=True)
        status[dbsettings.Status.DISCARDED.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.DISCARDED, uuid=uuid, sorting_desc=True)
        status[dbsettings.Status.FINISHED.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.FINISHED, uuid=uuid, sorting_desc=True)
        status[dbsettings.Status.DISCOVERING.name] = \
            dbutils.get_sites_by_processing_status(s_status=dbsettings.Status.DISCOVERING, uuid=uuid, sorting_desc=True)

    return status


def generate_uuid():

    """
    Generate UUID from current timestamp and MAC address

    :return: UUID - UUID (https://docs.python.org/2/library/uuid.html)
    """

    return uuid.uuid1()
