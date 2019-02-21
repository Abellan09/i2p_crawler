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
import dbsettings
import dbutils

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
    for status in dbsettings.SITE_STATUS_DEFAULT_INFO.keys():
        entities.SiteStatus(type=status, description=dbsettings.SITE_STATUS_DEFAULT_INFO[status])


def add_default_site_types():
    """
    Adds default types of sites found. (See NT_DEFAULT_INFO at settings.py)

    """
    for type in dbsettings.SITE_TYPE_DEFAULT_INFO.keys():
        entities.SiteType(type=type, description=dbsettings.SITE_TYPE_DEFAULT_INFO[type])

def add_fake_discovery_info():
    """
    Adds default discovery info just for testing dicovering procedure
    """

    valid_site = 'no.i2p'
    dbutils.create_site(valid_site)
    dbutils.set_site_current_processing_status(s_url=valid_site, s_status=dbsettings.Status.DISCOVERING)

    not_valid_site = 'fake.i2p'
    dbutils.create_site(not_valid_site)
    dbutils.set_site_current_processing_status(s_url=not_valid_site, s_status=dbsettings.Status.DISCOVERING)

    # Simulates the discovering process
    # Valid site
    # Discovering process of valid site got 2xx o 3xx http status
    dbutils.set_site_current_processing_status(s_url=valid_site, s_status=dbsettings.Status.PENDING,
                                               s_http_status='200')

    # Fake site
    # Discovering process of fake site got 4xx o 5xx http status
    dbutils.set_site_current_processing_status(s_url=not_valid_site, s_status=dbsettings.Status.DISCOVERING,
                                               s_http_status='500')


def add_default_languages():
    #TODO populate all languages
    pass

def main():
    """
    Creates the schema and adds initial default info.

    """
    with db_session:
        add_default_info()
        add_fake_discovery_info()

if __name__ == '__main__':
    main()