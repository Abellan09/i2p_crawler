from pony.orm import *
from database import dbutils
from database import entities
from datetime import datetime

# pony SQL debug
set_sql_debug(True)

# Set default info into the database
dbutils.add_default_info()

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

