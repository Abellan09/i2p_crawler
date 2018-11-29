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



def add_default_info():
    """
    Adds default information to the database

    """
    # Adding node types
    add_default_node_types()
    # Adding node status
    add_default_node_status()



def add_default_node_status():
    """
    Adds default status for node crawling. (See NS_DEFAULT_INFO at settings.py)

    """
    for status in settings.NS_DEFAULT_INFO.keys():
        entities.NodeStatus(type=status, description=settings.NS_DEFAULT_INFO[status])



def add_default_node_types():
    """
    Adds default types of nodes found. (See NT_DEFAULT_INFO at settings.py)

    """
    for type in settings.NT_DEFAULT_INFO.keys():
        entities.NodeType(type=type, description=settings.NT_DEFAULT_INFO[type])


# NODE ENTITY - CRUD (Create Read Update Delete)
def create_node(n_url, n_type=settings.NT_COD_I2P, n_status=settings.NS_COD_ONGOING):
    """
    Creates a new node. If no type and status is provided, I2P and Ongoing status are setup

    :param n_url: str - URL of the site, which will the name of the new node
    :param n_type: str - Type of the new node
    :param n_status: str - Processing status of the new node

    :return: Node - The new node if the node does not exist. Otherwise, return None
    """
    if not entities.Node.exists(name=n_url):
        # Gets the node type
        type = entities.NodeType.get(type=n_type)
        # Gets the processing status
        status = entities.NodeStatus.get(type=n_status)
        # Creates the new node and returns it
        return entities.Node(name=n_url, type=type, status=status)
    else:
        return None


def get_node(n_url):
    """
    Gets the node by its URL which is the name of the node

    :param n_url: str - URL/name of the node
    :return: Node - The node or None if it was not found.
    """
    # Gets the node by url
    return entities.Node.get(name=n_url)

def get_nodes():
    """
    Gets all nodes

    :return: list - list of nodes
    """

    return entities.Node.select()[:]


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


def set_node_status(n_url, n_status=settings.NS_COD_ONGOING):
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
        node.status = entities.NodeStatus.get(type=n_status)
    return node


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
        node.type = entities.NodeType.get(type=n_type)
    return node


# NODE LINK STATS - CRUD (Create Read Update Delete)
def set_statistics(n_url, n_incoming, n_outgoing, n_degree):
    """
    Creates or updates node statistics

    :param n_url: str - URL/name of the node
    :param n_incoming: int - # of incoming links
    :param n_outgoing: int - # of outgoing links
    :param n_degree: int - node degree
    :return: NodeConnectivitySummary - The node statistics
    """
    # Gets the node
    node = entities.Node.get(name=n_url)
    # If the node exists
    if isinstance(node, entities.Node):
        # If the node has statistics, we are going to update values
        if isinstance(node.connectivity_summary,entities.NodeConnectivitySummary):
            node.connectivity_summary.incoming = n_incoming
            node.connectivity_summary.outgoing = n_outgoing
            node.connectivity_summary.degree = n_degree
        else:
            # set statistics
            entities.NodeConnectivitySummary(node=node, incoming=n_incoming, outgoing=n_outgoing, degree=n_degree)

    return node.connectivity_summary


def delete_statistics(n_url):
    """
    Deletes the node statistics

    :param n_url: str - URL/name of the node
    """
    # Gets the node
    node = entities.Node.get(name=n_url)
    # If the node exists
    if isinstance(node, entities.Node):
        # Delete its statistics
        node.connectivity_summary.delete()

# NODE LINKS - CRUD (Create Read Update Delete)
def create_link(sn_url, tn_url):
    """
    Creates a link if and only if both nodes, source and destination node, exist.

    :param sn_url: str - URL/name of the source node
    :param tn_url: str - URL/name of the destination node
    :return: The created link or None, if the link could not be created.
    """

    # Gets source node
    s_node = entities.Node.get(name=sn_url)
    if not isinstance(s_node, entities.Node):
        # if the source node does not exists
        return None
    # Gets destination node
    t_node = entities.Node.get(name=tn_url)
    if not isinstance(t_node, entities.Node):
        # if the destination node does not exists
        return None

    # Does the link exists?
    # FIXME: Check if the link exists?
    # link = entities.NodeLink.get(src_node=s_node)
    # if not isinstance(link, entities.NodeLink):
    # Creates the link
    link = entities.NodeLink(src_node=s_node, dst_node=t_node)

    return link


def get_incoming_links(tn_url):
    """
    Gets all incoming links to a destination node

    :param tn_url: str - URL/name of the destination node
    :return: list of NodeLink
    """
    incoming = select(
        link for link in entities.NodeLink for dst_node in link.dst_node if dst_node.name == tn_url)[:]
    return incoming


def get_outgoing_links(sn_url):
    """
    Gets all outgoing links from a source node

    :param sn_url: str - URL/name of the source node
    :return: list of NodeLink
    """
    outgoing = select(
        link for link in entities.NodeLink for src_node in link.src_node if src_node.name == sn_url)[:]
    return outgoing


def delete_links(n_url):
    """
    Deletes all links to and from a specific node

    :param n_url: tr - URL/name of the node
    """
    # Delete incoming links
    incoming = get_incoming_links(n_url)
    [link.delete() for link in incoming]

    # Delete outgoing links
    outgoing = get_outgoing_links(n_url)
    [link.delete() for link in outgoing]


def set_qos_to_node_by_node_name(node_name, qos):
    # Get the corresponding node
    qos = entities.NodeQoS(timestamp=datetime.today(), delay=qos)
    node = entities.Node.get(name=node_name)
    qos.node = node
