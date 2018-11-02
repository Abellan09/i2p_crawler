from pony.orm import *
import entities

@db_session
def add_default_info():
    typeTOR = entities.NodeType(type='TOR',description='TOR external link')
    statusRunning = entities.NodeStatus(type='Running',description= 'The crawler is getting info from this node.')
    target_node = entities.Node(name="http://i2ptarget.onion",node_type=typeTOR,node_status=statusRunning)
    src_node = entities.Node(name="http://i2psrc.onion", node_type=typeTOR, node_status=statusRunning)
    entities.NodeLink(target_node=target_node,src_node=src_node)

add_default_info()