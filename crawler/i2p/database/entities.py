# -*- coding: utf-8 -*-

"""
    :mod:`entities`
    ===========================================================================
    :synopsis: Declares ORM entities and their relationships
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

from pony.orm import *
from datetime import datetime

db = Database()

#TODO: move this to a config file
db.bind(provider='mysql', host='localhost', user='root', passwd='root', db='i2p_database')


class Site(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    type = Optional('SiteType')
    processing_status = Set('SiteProcessingStatus')
    connectivity_summary = Optional('SiteConnectivitySummary')
    footprint = Optional('SiteFootprint')
    src_link = Set('Link', reverse='src_site')
    dst_link = Set('Link', reverse='dst_site')
    categories = Set('SiteCategory')
    languages = Set('SiteLanguage')
    qos = Set('SiteQoS')


class SiteType(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str,unique=True)
    description = Optional(str)
    site = Optional('Site')


class SiteStatus(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str,unique=True)
    description = Optional(str)
    status = Optional('SiteProcessingStatus')


class SiteProcessingStatus(db.Entity):
    id = PrimaryKey(int, auto=True)
    status = Optional('SiteStatus')
    site = Optional('Site')
    timestamp = Required(datetime)


class SiteConnectivitySummary(db.Entity):
    id = PrimaryKey(int, auto=True)
    outgoing = Optional(int, default=0)
    incoming = Optional(int, default=0)
    degree = Optional(int, default=0)
    site = Required('Site')


class Link(db.Entity):
    id = PrimaryKey(int, auto=True)
    src_site = Set('Site', reverse='src_link')
    dst_site = Set('Site', reverse='dst_link')


class SiteCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Optional(str)
    sites = Set('Site')


class SiteLanguage(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Optional(str)
    sites = Set('Site')
    variant = Optional(str)


class SiteQoS(db.Entity):
    id = PrimaryKey(int, auto=True)
    timestamp = Required(datetime)
    delay = Optional(float)
    site = Required('Site')


class SiteFootprint(db.Entity):
    id = PrimaryKey(int, auto=True)
    http_headers = Optional(str)
    meta = Optional(str)
    site = Required('Site')

# Creates tablas from the above entities if they do not exist
db.generate_mapping(create_tables=True)