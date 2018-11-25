from pony.orm import *
from database import dbutils
from database import entities
from datetime import datetime
from database import settings

# pony SQL debug
#set_sql_debug(True)

# Set default info into the database
#dbutils.add_default_info()

# An example of how to set and get an entity info
#dbutils.add_fake_links()
#dbutils.get_nodelink_info(id=1)

# Getting all node links
#nodelinks = dbutils.get_all_nodelinks()

# Getting all incoming links for a node
#incoming = dbutils.get_incoming_node_links(node_id=1)
#print(len(incoming))

# Inserting a QoS results for a node
# Setting up the QoS entity results
#dbutils.set_qos_to_node_by_node_name('http://i2ptarget.i2p',10.3)

# Node tests
#dbutils.create_node("i2ptracker_src.i2p")
#[dbutils.create_node("i2ptracker_target_"+str(i)+".i2p") for i in range(1,4)]

#dbutils.delete_node("i2ptracker.i2p")

#print(dbutils.get_node("i2ptracker.i2p").name)

#dbutils.set_node_status("i2ptracker.i2p",settings.NS_COD_PENDING)
#dbutils.set_node_type("i2ptracker.i2p",settings.NT_COD_SURFACE)

# Link tests
#link = dbutils.create_link("i2ptracker_src.i2p","i2ptracker_src.i2p")
#link = dbutils.create_link("i2ptracker_src.i2p","i2ptracker_target_1.i2p")
#link = dbutils.create_link("i2ptracker_src.i2p","i2ptracker_target_2.i2p")
#link = dbutils.create_link("i2ptracker_src.i2p","i2ptracker_target_3.i2p")

dbutils.delete_links("i2ptracker_src.i2p")

with db_session:
    links = dbutils.get_incoming_links("i2ptracker_target_2.i2p")
    print(links)
    for link in links:
        #print([node.name for node in link.src_node])
        print([node.name for node in link.src_node])

    links = dbutils.get_outcoming_links("i2ptracker_src.i2p")
    print(links)
    for link in links:
        print([node.name for node in link.target_node])
        #print([node.name for node in link.target_node])