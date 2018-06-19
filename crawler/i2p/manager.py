# encoding: utf-8

import os			# https://docs.python.org/2/library/os.html
import shutil		# https://docs.python.org/2/library/shutil.html
import time			# https://docs.python.org/2/library/time.html
import subprocess	# https://docs.python.org/2/library/subprocess.html
import urlparse		# https://docs.python.org/2/library/urlparse.html
import copy			# https://docs.python.org/2/library/copy.html
import sqlite3		# https://docs.python.org/2/library/sqlite3.html
import json			# https://docs.python.org/2/library/json.html

def throw_crawler():
	'''
	EN: It runs an instance of spider.py (if applicable).
	SP: Lanza una instancia de spider.py (si procede).
	
	If the maximum number of allowed concurrent crawlers has not been exceeded, a subprocess of spider.py is
	launched to crawl the next contained eepsite in the pending_sites list.
	Si no se ha sobrepasado el número máximo de crawlers concurrentes permitidos, se lanza un subproceso de 
	spider.py para crawlear el siguiente eepsite contenido en la lista pending_sites.
	'''
	#print("DEBUG - Dentro throw_crawler()")
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	global maximum_crawlers
	global total_crawlers
	if (ongoing_crawlers < maximum_crawlers):
		#print("DEBUG - Dentro if")
		next_site = pending_sites.pop()
		ongoing_sites.append(next_site)
		param1 = "url=http://" + next_site
		param2 = "i2p/spiders/ongoing/" + next_site + ".json"
		#print(param1)
		#print(param2)
		#subprocess.call(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2], shell=False)
		subprocess.Popen(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2 ], shell=False)
		ongoing_crawlers += 1
		total_crawlers += 1

def check():
	'''
	EN: It checks if in the /finished directory there are ".fail" and/or ".ok" files to process.
	SP: Comprueba si en el directorio /finished hay ficheros ".fail" y/o ".ok" que procesar.
	
	It adds the names of the ".ok" and ".fail" files to the ok_files and fail_files lists, respectively.
	After that, it calls the process_fail() and process_ok() functions.
	Añade los nombres de los ficheros ".ok" y ".fail" a las listas ok_files y fail_files, respectivamente.
	A continuación, llama a las funciones process_fail() y process_ok().
	'''
	#print("DEBUG - Dentro de check()")
	global ok_files
	global fail_files
	finished_files = os.listdir("i2p/spiders/finished")
	for fil in finished_files:
		if fil.endswith(".ok"):
			ok_files.append(fil)
		elif fil.endswith(".fail"):
			fail_files.append(fil)	
	#print ("DEBUG - " + finished_files)
	process_fail()
	process_ok()

def process_fail():
	'''
	EN: It processes the files with ".fail" extension.
	SP: Procesa los ficheros con extensión ".fail".
	
	It deletes the files with the ".fail" extension from the /finished directory and adds the failed site
	to the pending_sites list so that the site can be crawled again.
	Elimina los ficheros con extensión ".fail" del directorio /finished y añade el site fallido a la lista
	pending_sites para que se vuelva a crawlear.
	'''
	print("DEBUG - Dentro de process_fail()")
	global fail_files
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	files_to_remove = []
	print("DEBUG - Fail_files antes del bucle: " + str(fail_files))
	try:
		for fil in fail_files:
			files_to_remove.append(fil)
			eliminar = "i2p/spiders/ongoing/" + fil.replace(".fail", ".json")
			os.remove(eliminar)
			eliminar = "i2p/spiders/finished/" + fil
			os.remove(eliminar)
			fil_without_extension = fil.replace(".fail", "")
			ongoing_sites.remove(fil_without_extension)
			ongoing_crawlers -= 1
			if fil_without_extension not in pending_sites:
				pending_sites.append(fil_without_extension)
				print("DEBUG - " + fil_without_extension + " add to pending_sites")
		#print ("Files to remove: " + str(files_to_remove))
	except Exception as e:
		print("ERROR - Se ha producido algun error al intentar borrar los archivos")
	finally:
		for i in files_to_remove:
			fail_files.remove(i)
		print("DEBUG - Fail_files despues del bucle: " + str(fail_files))
	
def process_ok():
	'''
	EN: It processes the files with ".ok" extension.
	SP: Procesa los ficheros con extensión ".ok".
	
	It moves the ".json" files of the sites that have been crawled correctly (.ok) from the /ongoing directory to 
	the /finished directory, opens said ".json" files and adds the pertinent data to db_dictionary, adds the sites 
	that haven't been visited yet to the pending_sites and deletes the ".ok" files once processed.
	Mueve los ficheros ".json" de los sites que han sido crawleados correctamente (.ok) del directorio /ongoing
	al directorio /finished, abre dichos ficheros ".json" y añade a db_dictionary los datos pertinentes, añade
	a pending_sites los sites que no se hayan visitado y borra los ficheros ".ok" una vez procesados.
	'''
	print("DEBUG - Dentro de process_ok()")
	global db_dictionary
	global ok_files
	global visited_sites
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	files_to_remove = []
	print("DEBUG - ok_files antes del bucle: " + str(ok_files))
	try:
		for fil in ok_files:
			files_to_remove.append(fil)
			fil_without_extension = fil.replace(".ok", "")
			fil_json_extension = fil.replace(".ok", ".json")
			source = "i2p/spiders/ongoing/" + fil_json_extension
			target = "i2p/spiders/finished/" + fil_json_extension
			shutil.move(source, target)
			ongoing_sites.remove(fil_without_extension)
			ongoing_crawlers -= 1
			with open(target) as f:
				crawled_items = json.load(f)
			crawled_eepsites = crawled_items[len(crawled_items) - 1]["extracted_eepsites"]
			print("INFO - Extracted eepsites from " + fil + ": " + str(crawled_eepsites))
			if fil_without_extension not in visited_sites:
				visited_sites.append(fil_without_extension)
				db_dictionary[fil_without_extension]=crawled_eepsites
				print db_dictionary
			for site in crawled_eepsites:
				if (site not in pending_sites) and (site not in ongoing_sites) and (site not in visited_sites) and (site endswith(".i2p")):
					pending_sites.append(site)
					#print site
					print("DEBUG - " + site + " add to pending_sites")
			eliminar = "i2p/spiders/finished/" + fil
			os.remove(eliminar)
	except:
		print("ERROR - Se ha producido algun error al intentar borrar los archivos")
	finally:
		for i in files_to_remove:
			ok_files.remove(i)
		print("DEBUG - ok_files despues del bucle: " + str(ok_files))
		
def add_to_database():
	'''
	EN: It adds the extracted data by the crawler to the database.
	SP: Añade los datos extraídos por el crawler a la base de datos.
	
	First, it fills in some fields of the table "nodes" (name and outgoing_sites), then it fills in all the fields
	of the "links" table, and finally, it fills in the incoming_sites and degree fields of the table "nodes".
	En primer lugar, rellena algunos campos de la tabla "nodes" (name y outgoing_sites), después rellena
	todos los campos de la tabla "links", y finalmente, rellena los campos incoming_sites y degree de la
	tabla "nodes".
	'''
	global db_dictionary
	for key in db_dictionary:
		#print key, ":", db_dictionary[key]
		source = key
		targets = db_dictionary[key]
		add_nodes_to_database(source, len(targets))
	for key in db_dictionary:
		source = key
		targets = db_dictionary[key]
		#print targets
		#source_id = 0
		targets_id_aux = []
		try:
			connection = sqlite3.connect("i2p_database.db") # open the db
			cursor = connection.cursor() # get a cursor object
			cursor.execute("SELECT id FROM nodes WHERE name=?", (source,))
			source_id_aux = cursor.fetchone()
			for target in targets:
				cursor.execute("SELECT id FROM nodes WHERE name=?", (target,))
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
	add_degree_to_nodes()

def add_nodes_to_database(site, targeted_sites):
	'''
	EN: It adds to the table "nodes" the data of each site referring to the fields "name" and "outgoing_sites".
	SP: Añade a la tabla "nodes" los datos referentes a los campos "name" y "outgoing_sites" de cada site.
	'''
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
	'''
	EN: It adds to the table "links" the data of each site referring to the fields "source" and "target".
	SP: Añade a la tabla "links" los datos referentes a los campos "source" y "target" de cada site.
	'''
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

def add_degree_to_nodes():
	'''
	EN: It adds to the table "nodes" the data of each site referring to the fields "incoming_sites" and "degree".
	SP: Añade a la tabla "nodes" los datos referentes a los campos "incoming_sites" y "degree" de cada site.
	'''
	try:
		connection = sqlite3.connect("i2p_database.db") # open the db
		cursor = connection.cursor() # get a cursor object
		cursor.execute("SELECT id FROM nodes")
		nodes_ids_aux = cursor.fetchall()
		nodes_ids = []
		for i in nodes_ids_aux:
			nodes_ids.append(i[0])
		for ide in nodes_ids:
			print ide
			cursor.execute("SELECT id FROM links WHERE target=?", (ide,))
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

def set_degree(incoming_sites):
	'''
	EN: It assings a certain degree to a site depending on the sites that point at it.
	SP: Asigna un determinado grado a un site en función de los sites que lo apuntan.
	
	:param incoming_sites: number of sites that point to the site / número de sitios que apuntan al site
	:return: the assigned degree / el grado asignado
	'''
	degree = 3
	if incoming_sites >= 10:
		degree = 15
	elif incoming_sites >= 7:
		degree = 12
	elif incoming_sites >= 5:
		degree = 10
	elif incoming_sites >= 3:
		degree = 8
	elif incoming_sites >= 1:
		degree = 5
	print("DEGREE = " + str(degree))
	return degree

def results():
	'''
	EN: It shows some results about the execution of the script.
	SP: Muestra algunos resultados sobre la ejecución del script.
	
	It prints the total number of launched crawlers, as well as the total number of executions of the main program loop.
	Imprime el número total de crawlers lanzados, así como el número total de ejecuciones del bucle principal del programa.
	'''
	print("RESULT - Total Launched Crawlers: " + str(total_crawlers))
	print("RESULT - Total Loop Executions: " + str(total_loop_executions))


def dict_factory(cursor, row):
	'''
	EN: Function taken from https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
	SP: Función tomada de https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
	'''
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def db_to_json():
	'''
	EN: It generates a file in json format with the nodes and links that are contained in the database.
	SP: Genera un archivo en formato json con los nodos y links contenidos en la base de datos.
	'''
	connection = sqlite3.connect("i2p_database.db")
	connection.row_factory = dict_factory
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM nodes ORDER BY id")
	nodes = cursor.fetchall()
	cursor.execute("SELECT * FROM links ORDER BY source")
	links = cursor.fetchall()
	json_result = json.dumps({"nodes": nodes, "links": links}, sort_keys=True, indent=4, separators=(',', ': '))
	print json_result
	with open('i2p_data.json', 'wb') as f:
		f.write(json_result)

seed_sites = [
	"identiguy.i2p",
	"secure.thetinhat.i2p",
	"i2pwiki.i2p",
	"i2p-projekt.i2p",
	"echelon.i2p",
	"exchanged.i2p",
	"zzz.i2p",
	"planet.i2p",
	"zerobin.i2p",
	"i2pforum.i2p",
	"stats.i2p",
	"anoncoin.i2p",
	"i2pdarknetmap.i2p",
]
visited_sites = []
ongoing_sites = []
pending_sites = []
pending_sites = copy.deepcopy(seed_sites)
maximum_crawlers = 10
ongoing_crawlers = 0
total_crawlers = 0
total_loop_executions = 0
ok_files = []
fail_files = []
db_dictionary = {}

def main():
	'''
	EN: It controls the whole process of the crawling through a loop that is repeated every 2 seconds.
	SP: Controla todo el proceso del crawling mediante un bucle que se repite cada 2 segundos.
	
	Every two seconds it enters the main loop (if there are still sites to visit or sites that are been visited) to crawl all the sites.
	Finally, the extracted info is added to the database and the json file that will be used for web visualitation of the node map is generated.
	Cada dos segundos se entra en el bucle principal (si quedan sitios por visitar o se están visitando) para crawlear todos los sites.
	Finalmente, la información extraída se añade a la base de datos y se genera el archivo json que se utilizará para la visulación web del mapa de nodos.
	'''
	global total_loop_executions
	global ongoing_crawlers
	global pending_sites
	global visited_sites
	global ongoing_sites
	while pending_sites or ongoing_sites:
		print("INFO - Ongoing_crawlers: " + str(ongoing_crawlers))
		#print(time.strftime("DEBUG - Time: " + "%H:%M:%S", time.gmtime()))
		print("DEBUG - Pending sites: " + str(pending_sites))
		print("DEBUG - Finished sites: " + str(visited_sites))
		print("DEBUG - Ongoing sites: " + str(ongoing_sites))
		throw_crawler()
		check()
		total_loop_executions += 1
		time.sleep(1) # duerme 2 segundos
	add_to_database()
	db_to_json()
	results()

if __name__ == '__main__':
    main()
