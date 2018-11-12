from pony.orm import *
from datetime import datetime

db = Database()
db.bind(provider='mysql', host='localhost', user='root', passwd='root', db='i2p_database')

class Node(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    node_type = Required('NodeType')
    node_status = Required('NodeStatus')
    node_link_stat = Optional('NodeLinkStat')
    node_category = Optional('NodeCategory')
    node_language = Optional('NodeLanguage')
    node_qos = Optional('NodeQoS')
    node_footprinting = Optional('NodeFootprinting')
    src_links = Set('NodeLink', reverse='src_node')
    target_link = Set('NodeLink', reverse='target_node')


class NodeType(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str)
    description = Optional(str)
    nodes = Set(Node)


class NodeStatus(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str)
    description = Optional(str)
    nodes = Set(Node)


class NodeLinkStat(db.Entity):
    id = PrimaryKey(int, auto=True)
    outgoing = Optional(int, default=0)
    incoming = Optional(int, default=0)
    degree = Optional(int, default=0)
    node = Required(Node)


class NodeLink(db.Entity):
    id = PrimaryKey(int, auto=True)
    src_node = Set(Node, reverse='src_links')
    target_node = Set(Node, reverse='target_link')


class NodeCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    description = Optional(str)
    nodes = Set(Node)


class NodeLanguage(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    description = Optional(str)
    nodes = Set(Node)


class NodeQoS(db.Entity):
    id = PrimaryKey(int, auto=True)
    timestamp = Required(datetime)
    delay = Optional(float)
    node = Optional(Node)


class NodeFootprinting(db.Entity):
    id = PrimaryKey(int, auto=True)
    http_headers = Optional(str)
    meta = Optional(str)
    node = Optional(Node)

# Creates tablas from the above entities if they do not exist
db.generate_mapping(create_tables=True)