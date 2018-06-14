import sqlite3

diccionario = {
	"anoncoin.i2p": ["pepito.i2p", "beibe.i2p"], 
	"beibe.i2p": [],
	"pepito.i2p": ["ggeasy.i2p", "anoncoin.i2p", "beibe.i2p"],
	"ggeasy.i2p": ["pepito.i2p"],
}

#print diccionario

def add_to_database():
	print("DEBUG - Dentro de add_to_database()")
	for key in diccionario:
		#print key, ":", diccionario[key]
		source = key
		targets = diccionario[key]
		add_nodes_to_database(source, len(targets))
	for key in diccionario:
		source = key
		targets = diccionario[key]
		#print targets
		#source_id = 0
		targets_id_aux = []
		try:
			connection = sqlite3.connect("i2p_database.db") # open the db
			cursor = connection.cursor() # get a cursor object
			cursor.execute("select id from nodes where name=?", (source,))
			source_id_aux = cursor.fetchone()
			for target in targets:
				cursor.execute("select id from nodes where name=?", (target,))
				target_id = cursor.fetchone()
				targets_id_aux.append(target_id)
		except sqlite3.DatabaseError as e:
			print("ERROR - Something was wrong with the Database")
			connection.rollback() # roll back any change if something goes wrong
			raise e
		finally:
			connection.close() # close the db connection
		source_id = source_id_aux[0]
		targets_id = []
		for i in targets_id_aux:
			targets_id.append(i[0])
		print ("DEBUG - Source_ID = " + str(source_id))
		print ("DEBUG - Targets_ID = " + str(targets_id))
		add_links_to_database(source_id, targets_id)

def add_nodes_to_database(site, targeted_sites):
	print("DEBUG - Dentro de add_nodes_to_database()")
	name = site
	outgoing_sites = targeted_sites
	try:
		connection = sqlite3.connect("i2p_database.db") # open the db
		cursor = connection.cursor() # get a cursor object
		cursor.execute('''INSERT INTO nodes(name, outgoing_sites)
						VALUES(?,?)''', (name, outgoing_sites))
		connection.commit() # commit the change(s)
	except sqlite3.DatabaseError as e:
		print("ERROR - Something was wrong with the Database")
		connection.rollback() # roll back any change if something goes wrong
		raise e
	finally:
		connection.close() # close the db connection

def add_links_to_database(source_id, targets_id):
	print("DEBUG - Dentro de add_links_to_database()")
	try:
		connection = sqlite3.connect("i2p_database.db") # open the db
		cursor = connection.cursor() # get a cursor object
		for target_id in targets_id:
			cursor.execute('''INSERT INTO links(source, target)
						VALUES(?,?)''', (source_id, target_id))
		connection.commit() # commit the change(s)
	except sqlite3.DatabaseError as e:
		print("ERROR - Something was wrong with the Database")
		connection.rollback() # roll back any change if something goes wrong
		raise e
	finally:
		connection.close() # close the db connection

add_to_database()
