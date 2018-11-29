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

class Node(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    type = Optional('NodeType')
    status = Optional('NodeStatus')
    connectivity_summary = Optional('NodeConnectivitySummary')
    footprinting = Optional('NodeFootprinting')
    src_link = Set('NodeLink', reverse='src_node')
    dst_link = Set('NodeLink', reverse='dst_node')
    categories = Set('NodeCategory')
    languages = Set('NodeLanguage')
    qos = Set('NodeQoS')


class NodeType(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str,unique=True)
    description = Optional(str)
    node = Optional(Node)


class NodeStatus(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str,unique=True)
    description = Optional(str)
    node = Optional(Node)


class NodeConnectivitySummary(db.Entity):
    id = PrimaryKey(int, auto=True)
    outgoing = Optional(int, default=0)
    incoming = Optional(int, default=0)
    degree = Optional(int, default=0)
    node = Required(Node)


class NodeLink(db.Entity):
    id = PrimaryKey(int, auto=True)
    src_node = Set(Node, reverse='src_link')
    dst_node = Set(Node, reverse='dst_link')


class NodeCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Optional(str)
    nodes = Set(Node)


class NodeLanguage(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Optional(str)
    nodes = Set(Node)
    variant = Optional(str)


class NodeQoS(db.Entity):
    id = PrimaryKey(int, auto=True)
    timestamp = Required(datetime)
    delay = Optional(float)
    node = Required(Node)


class NodeFootprinting(db.Entity):
    id = PrimaryKey(int, auto=True)
    http_headers = Optional(str)
    meta = Optional(str)
    node = Required(Node)

# Creates tablas from the above entities if they do not exist
db.generate_mapping(create_tables=True)