import sqlite3

def set_degree(incoming_sites):
	degree = 3
	if incoming_sites > 1:
		degree = 5
	elif incoming_sites >= 3:
		degree = 8
	elif incoming_sites >= 5:
		degree = 10
	elif incoming_sites >= 7:
		degree = 12
	elif incoming_sites >= 10:
		degree = 15
	print("DEGREE = " + str(degree))
	return degree

try:
	connection = sqlite3.connect("i2p_database.db") # open the db
	cursor = connection.cursor() # get a cursor object
	cursor.execute("select id from nodes")
	nodes_ids_aux = cursor.fetchall()
	nodes_ids = []
	for i in nodes_ids_aux:
		nodes_ids.append(i[0])
	for ide in nodes_ids:
		print ide
		cursor.execute("select id from links where target=?", (ide,))
		resultado = cursor.fetchall()
		incoming_sites = len(resultado)
		degree = set_degree(incoming_sites)
		print incoming_sites
		print degree
		cursor.execute('''UPDATE nodes SET incoming_sites=?, degree=?
						WHERE nodes.id=?''', (incoming_sites, degree, ide))
		connection.commit()
except sqlite3.DatabaseError as e:
	print("ERROR - Something was wrong with the Database")
	connection.rollback() # roll back any change if something goes wrong
	raise e
finally:
	connection.close() # close the db connection
print nodes_ids
