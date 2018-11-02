from pony.orm import *
from database import dbutils

# pony SQL debug
set_sql_debug(True)

# Set default info into the database
dbutils.add_default_info()

# An example of how to set and get an entity info
dbutils.add_fake_link()
dbutils.get_nodelink_info(id=1)


