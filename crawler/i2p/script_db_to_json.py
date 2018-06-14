import sqlite3
import json

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

connection = sqlite3.connect("i2p_database.db")
connection.row_factory = dict_factory
cursor = connection.cursor()

cursor.execute("select * from nodes order by id")
nodes = cursor.fetchall()

cursor.execute("select * from links order by source")
links = cursor.fetchall()

json_result = json.dumps({"nodes": nodes, "links": links}, sort_keys=True, indent=4, separators=(',', ': '))
print json_result

with open('i2p_data.json', 'wb') as f:
	f.write(json_result)
