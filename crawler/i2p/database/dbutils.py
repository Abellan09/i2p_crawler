# -*- coding: utf-8 -*-

"""
    :mod:`dbutils`
    ===========================================================================
    :synopsis: API to talk to database
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

from pony.orm import *
from datetime import datetime
import entities
import settings

@db_session
def add_default_info():
    """
    Adds default information to the database

    """
    # Adding node types
    add_default_node_types()
    # Adding node status
    add_default_node_status()

@db_session
def add_default_node_status():
    """
    Adds default status for node crawling. (See NS_DEFAULT_INFO at settings.py)

    """
    for status in settings.NS_DEFAULT_INFO.keys():
        entities.NodeStatus(type=status,description=settings.NS_DEFAULT_INFO[status])

@db_session
def add_default_node_types():
    """
    Adds default types of nodes found. (See NT_DEFAULT_INFO at settings.py)

    """
    for type in settings.NT_DEFAULT_INFO.keys():
        entities.NodeType(type=type,description=settings.NT_DEFAULT_INFO[type])

@db_session
def add_fake_links():
    target_node = entities.Node(name="http://i2ptarget.i2p",
                                node_type=entities.NodeType[1],
                                node_status=entities.NodeStatus[1])
    src_node = entities.Node(name="http://i2src.onion",
                                node_type=entities.NodeType[2],
                                node_status=entities.NodeStatus[2])
    another_src_node = entities.Node(name="http://i2anothersrc.surface",
                             node_type=entities.NodeType[3],
                             node_status=entities.NodeStatus[3])
    entities.NodeLink(target_node=target_node,src_node=src_node)
    entities.NodeLink(target_node=target_node, src_node=another_src_node)

@db_session
def get_nodelink_info(id):
    nl = entities.NodeLink[id]
    for nodes in nl.src_node:
        print(nodes.to_dict())

@db_session
def get_all_nodelinks():
    nodelinks = select(link for link in entities.NodeLink)[:]
    return nodelinks

@db_session
def get_incoming_node_links(node_id):
    incoming = select(link for link in entities.NodeLink for target_node in link.target_node if target_node.id == node_id)[:]
    return incoming

# NODE ENTITY - CRUD (Create Read Update Delete)
@db_session
def create_node(n_url,n_type=settings.NT_COD_I2P,n_status=settings.NS_COD_ONGOING):
    """
    Creates a new node. If no type and status is provided, I2P and Ongoing status are setup

    :param n_url: str - URL of the site, which will the name of the new node
    :param n_type: str - Type of the new node
    :param n_status: str - Processing status of the new node

    :return: Node - The new node
    """
    # Gets the node type
    node_type = entities.NodeType.get(type=n_type)
    # Gets the processing status
    node_status = entities.NodeStatus.get(type=n_status)
    # Creates the new node and returns it
    return entities.Node(name=n_url,node_type=node_type,node_status=node_status)

@db_session
def get_node(n_url):
    """
    Gets the node by its URL which is the name of the node

    :param n_url: str - URL/name of the node
    :return: Node - The node or None if it was not found.
    """
    # Gets the node by url
    return entities.Node.get(name=n_url)

@db_session
def delete_node(n_url):
    """
    Deletes the node by its URL which is the name of the node if it exists.

    :param n_url: str - URL/name of the node
    """
    # Gets the node to delete
    node = entities.Node.get(name=n_url)
    # If the node exists
    if isinstance(node, entities.Node):
        node.delete()

@db_session
def set_node_status(n_url,n_status=settings.NS_COD_ONGOING):
    """
    Set a new status of a node if it exists

    :param n_url: str - URL/name of the node
    :param n_status: str - The new processing status

    :return: Node - The updated node or None if the node does not exists
    """
    # Gets the node to update
    node = entities.Node.get(name=n_url)
    # If the node exists
    if isinstance(node, entities.Node):
        # Get and set the new estatus
        node.node_status = entities.NodeStatus.get(type=n_status)
    return node

@db_session
def set_node_type(n_url, n_type=settings.NT_COD_I2P):
    """
    Set a new type of a node if it exists

    :param n_url: str - URL/name of the node
    :param n_type: str - Type of the new node

    :return: Node - The updated node or None if the node does not exists
    """
    # Gets the node to update
    node = entities.Node.get(name=n_url)
    # If the node exists
    if isinstance(node, entities.Node):
        # Get and set the new type
        node.node_type = entities.NodeType.get(type=n_type)
    return node


@db_session
def set_qos_to_node_by_node_name(node_name,qos):
    # Get the corresponding node
    qos = entities.NodeQoS(timestamp=datetime.today(), delay=qos)
    node = entities.Node.get(name=node_name)
    qos.node = node


