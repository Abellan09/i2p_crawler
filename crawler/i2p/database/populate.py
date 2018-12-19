# -*- coding: utf-8 -*-

"""
    :mod:`populate`
    ===========================================================================
    :synopsis: populates database tables and adds default info
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

from pony.orm import sql_debug, db_session
import entities
import settings

sql_debug(True)

def add_default_info():
    """
    Adds default information to the database

    """
    # Adding site types
    add_default_site_types()
    # Adding site status
    add_default_site_status()


def add_default_site_status():
    """
    Adds default status for site crawling. (See NS_DEFAULT_INFO at settings.py)

    """
    for status in settings.SITE_STATUS_DEFAULT_INFO.keys():
        entities.SiteStatus(type=status, description=settings.SITE_STATUS_DEFAULT_INFO[status])


def add_default_site_types():
    """
    Adds default types of sites found. (See NT_DEFAULT_INFO at settings.py)

    """
    for type in settings.SITE_TYPE_DEFAULT_INFO.keys():
        entities.SiteType(type=type, description=settings.SITE_TYPE_DEFAULT_INFO[type])

def main():
    """
    Creates the schema and adds initial default info.

    """
    with db_session:
        add_default_info()

if __name__ == '__main__':
    main()