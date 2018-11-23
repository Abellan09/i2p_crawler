from pony.orm import *
import entities
from datetime import datetime

@db_session
def add_default_info():
    # Adding node types
    entities.NodeType(id=1,type='I2P',description='I2P site')
    entities.NodeType(id=2, type='TOR', description='TOR site')
    entities.NodeType(id=3, type='Surface', description='Surface site')
    # Adding node status
    entities.NodeStatus(id=1,type='Finished',description='The site has been succesfully crawled')
    entities.NodeStatus(id=2, type='Ongoing', description='The site is being crawled')
    entities.NodeStatus(id=3, type='Pending', description='Something was wrong with crawling process, so this site has be crawled again.')
    entities.NodeStatus(id=4, type='NotCrawleable', description='The site cannot be crawled')
    # Adding default categories
    entities.NodeCategory(id=1, name="Forum", description="Forum related category")
    entities.NodeCategory(id=2, name="Wiki", description="Wiki related category")

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

@db_session
def set_qos_to_node_by_node_name(node_name,qos):
    # Get the corresponding node
    qos = entities.NodeQoS(timestamp=datetime.today(), delay=qos)
    node = entities.Node.get(name=node_name)
    qos.node = node


