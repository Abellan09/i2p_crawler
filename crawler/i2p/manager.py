# encoding: utf-8

import os			# https://docs.python.org/2/library/os.html
import shutil		# https://docs.python.org/2/library/shutil.html
import time			# https://docs.python.org/2/library/time.html
import subprocess	# https://docs.python.org/2/library/subprocess.html
import urlparse		# https://docs.python.org/2/library/urlparse.html
import copy			# https://docs.python.org/2/library/copy.html
import sqlite3		# https://docs.python.org/2/library/sqlite3.html
import json			# https://docs.python.org/2/library/json.html
import logging		# https://docs.python.org/2/library/logging.html

from pony.orm import *
from database import dbutils
from database import settings

def throw_crawler():
	'''
	EN: It runs an instance of spider.py (if applicable).
	SP: Lanza una instancia de spider.py (si procede).
	
	If the maximum number of allowed concurrent crawlers has not been exceeded, a subprocess of spider.py is
	launched to crawl the next contained eepsite in the pending_sites list.
	Si no se ha sobrepasado el número máximo de crawlers concurrentes permitidos, se lanza un subproceso de 
	spider.py para crawlear el siguiente eepsite contenido en la lista pending_sites.
	'''
	logging.debug("Dentro de throw_crawler()")
	global ignored_sites
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	global maximum_crawlers
	global total_crawlers
	if (ongoing_crawlers <= maximum_crawlers) and (pending_sites):
		next_site = pending_sites.pop()
		if next_site in attempts_dict:
			attempts = attempts_dict.get(next_site)
			if (attempts > 5) and (next_site not in ignored_sites):
				ignored_sites.append(next_site)
			else:
				attempts_dict.update({next_site:attempts+1})
		else:
			attempts_dict.update({next_site:1})
		if(next_site not in ignored_sites):
			ongoing_sites.append(next_site)
			param1 = "url=http://" + next_site
			param2 = "i2p/spiders/ongoing/" + next_site + ".json"
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
	logging.debug("Dentro de check()")
	global ok_files
	global fail_files
	finished_files = os.listdir("i2p/spiders/finished")
	logging.debug("Finished Files: " + str(finished_files))
	for fil in finished_files:
		if (fil.endswith(".ok")) and (fil not in ok_files):
			ok_files.append(fil)
		elif (fil.endswith(".fail")) and (fil not in fail_files):
			fail_files.append(fil)	
		#finished_files.remove(fil)
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
	logging.debug("Dentro de process_fail()")
	global fail_files
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	files_to_remove = []
	logging.debug("Fail_files antes del bucle: " + str(fail_files))
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
				logging.debug(fil_without_extension + " add to pending_sites")
	except Exception as e:
		logging.error("There has been some error with the files")
	finally:
		for i in files_to_remove:
			fail_files.remove(i)
		logging.debug("Fail_files despues del bucle: " + str(fail_files))
	
def process_ok():
	'''
	EN: It processes the files with ".ok" extension.
	SP: Procesa los ficheros con extensión ".ok".
	
	It moves the ".json" files of the sites that have been crawled correctly (.ok) from the /ongoing directory to the /finished
	directory, opens said ".json" files, calls the add_to_database() function in order to add the pertinent data to database, 
	adds the sites that haven't been visited yet to the pending_sites and deletes the ".ok" files once processed.
	Mueve los ficheros ".json" de los sites que han sido crawleados correctamente (.ok) del directorio /ongoing	al directorio
	/finished, abre dichos ficheros ".json", llama a la función add_to_database() para añadir los datos pertinentes a la 
	base de datos, añade a pending_sites los sites que no se hayan visitado y borra los ficheros ".ok" una vez procesados.
	'''
	logging.debug("Dentro de process_ok()")
	global ok_files
	global visited_sites
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	files_to_remove = []
	logging.debug("ok_files antes del bucle: " + str(ok_files))
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
			logging.info("Extracted eepsites from " + fil + ": " + str(crawled_eepsites))
			if fil_without_extension not in visited_sites:
				visited_sites.append(fil_without_extension)
				add_to_database(fil_without_extension, crawled_eepsites)
			for site in crawled_eepsites:
				if (site not in pending_sites) and (site not in ongoing_sites) and (site not in visited_sites) and (site.endswith(".i2p")):
					pending_sites.append(site)
					logging.debug(site + " add to pending_sites")
			eliminar = "i2p/spiders/finished/" + fil
			os.remove(eliminar)
	except:
		logging.error("There has been some error with the files")
	finally:
		for i in files_to_remove:
			ok_files.remove(i)
		logging.debug("ok_files despues del bucle: " + str(ok_files))
		
def add_to_database(site, targeted_sites):
	'''
	EN: It adds the extracted data by the crawler to the database.
	SP: Añade los datos extraídos por el crawler a la base de datos.
	
	:param site: site in question to add to the database / site en cuestión a añadir a la base de datos
	:param targeted_sites: sites to which the site points at / sitios a los que el site apunta
	'''
	logging.debug("Dentro de add_to_database()")

	try:
		with db_session:
			# Creates the src site
			dbutils.create_site(site,s_status=settings.Status.FINISHED)

			for eepsite in targeted_sites:
				# Creates target sites
				dbutils.create_site(eepsite, s_type=settings.Type.I2P)
				# Linking all
				dbutils.create_link(site, eepsite)

	except Exception as e:
		logging.error("Something was wrong with the Database")
		raise e

def update_top():
	'''
	EN: It updates the TOP tables of sites with more incoming_sites (Table Incoming_Top) and with more outgoing_sites (Table Outgoing_Top).
	SP: Actualiza las tablas de los TOP de sites con más incoming_sites (Tabla Incoming_Top) y con más outgoing_sites (Tabla Outgoing_Top).
	'''
	logging.debug("Dentro de update_top()")
	try:
		connection = sqlite3.connect("../../www/i2p_database.db") # open the db
		cursor = connection.cursor() # get a cursor object
		cursor.execute("SELECT id, incoming_sites FROM nodes ORDER BY incoming_sites DESC LIMIT 5")
		incoming = cursor.fetchall()
		logging.debug("INCOMING: " + str(incoming))
		if (len(incoming)==5):
			for i in range(5):
				top_id = i+1
				node_id = incoming[i][0]
				cursor.execute("UPDATE incoming_top SET node_id=? WHERE id=?", (node_id, top_id,))
			logging.debug("The table Incoming_Top has been updated")
			cursor.execute("SELECT id, outgoing_sites FROM nodes ORDER BY outgoing_sites DESC LIMIT 5")
			outgoing = cursor.fetchall()
			for i in range(5):
				top_id = i+1
				node_id = outgoing[i][0]
				cursor.execute("UPDATE outgoing_top SET node_id=? WHERE id=?", (node_id, top_id,))
			logging.debug("The table Outgoing_Top has been updated")
			connection.commit() # commit the change(s)
	except sqlite3.DatabaseError as e:
		logging.error("Something was wrong with the Database")
		connection.rollback() # roll back any change if something goes wrong
		raise e
	finally:
		connection.close() # close the db connection

def results():
	'''
	EN: It shows some results about the execution of the script.
	SP: Muestra algunos resultados sobre la ejecución del script.
	
	It prints the total number of launched crawlers, as well as the total number of executions of the main program loop.
	Imprime el número total de crawlers lanzados, así como el número total de ejecuciones del bucle principal del programa.
	'''
	logging.debug("Dentro de results()")
	logging.info("Total Launched Crawlers: " + str(total_crawlers))
	logging.info("Total Loop Executions: " + str(total_loop_executions))

def dict_factory(cursor, row):
	'''
	EN: Function taken from https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
	SP: Función tomada de https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
	'''
	logging.debug("Dentro de dict_factory()")
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

seed_sites = []
ignored_sites = []
visited_sites = []
ongoing_sites = []
pending_sites = []
maximum_crawlers = 20
ongoing_crawlers = 0
total_crawlers = 0
total_loop_executions = 0
ok_files = []
fail_files = []
attempts_dict = {}

def main():
	'''
	EN: It controls the whole process of the crawling through a loop that is repeated every 2 seconds.
	SP: Controla todo el proceso del crawling mediante un bucle que se repite cada 2 segundos.
	
	Every second it enters the main loop (if there are still sites to visit or sites that are been visited) to crawl all the sites.
	Finally, the extracted info is added to the database and the json file that will be used for web visualitation of the node map is generated.
	Cada segundo se entra en el bucle principal (si quedan sitios por visitar o se están visitando) para crawlear todos los sites.
	Finalmente, la información extraída se añade a la base de datos y se genera el archivo json que se utilizará para la visulación web del mapa de nodos.
	'''
	logging.basicConfig(filename='registro.log',level=logging.DEBUG)
	logging.debug("Dentro de main()")
	global total_loop_executions
	global ongoing_crawlers
	global seed_sites
	global ignored_sites
	global pending_sites
	global visited_sites
	global ongoing_sites
	f = open("seed_urls.txt")
	line = f.readline()
	while line != "":
		line = line.replace("\n", "")
		seed_sites.append(line)
		line = f.readline()
	f.close()
	pending_sites=copy.deepcopy(seed_sites)
	time1 = time.time()
	time2 = time.time()
	while pending_sites or ongoing_sites:
		logging.info(time.strftime("Time: " + "%H:%M:%S", time.gmtime()))
		logging.info("Ongoing_crawlers: " + str(ongoing_crawlers))
		logging.debug("Pending sites: " + str(pending_sites))
		logging.debug("Finished sites: " + str(visited_sites))
		logging.debug("Ignored sites: " + str(ignored_sites))
		logging.debug("Ongoing sites: " + str(ongoing_sites))
		throw_crawler()
		check()
		total_loop_executions += 1
		time.sleep(1) # duerme 1 segundo
		if ((time2 - time1) < 60):
			time2 = time.time()
		else:
			time1 = time.time()
			time2 = time.time()
			update_top()
			results()

if __name__ == '__main__':
    main()
