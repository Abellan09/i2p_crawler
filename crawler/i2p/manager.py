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
		finished_files.remove(fil)
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
	name = site
	outgoing_sites = len(targeted_sites)
	try:
		connection = sqlite3.connect("C:\Program Files (x86)\Ampps\www\i2p_database.db") # open the db
		cursor = connection.cursor() # get a cursor object
		cursor.execute("SELECT name FROM nodes WHERE name=?", (name,))
		found = cursor.fetchone()
		if found is None:
			cursor.execute("INSERT INTO nodes(name, incoming_sites, outgoing_sites)	VALUES(?,?,?)", (name, 0, outgoing_sites))
		else:
			cursor.execute("UPDATE nodes SET outgoing_sites=? WHERE name=?", (outgoing_sites, name,))
		for iterator in range(len(targeted_sites)):
			cursor.execute("SELECT incoming_sites FROM nodes WHERE name=?", (targeted_sites[iterator],))
			found = cursor.fetchone()
			if found is None:
				cursor.execute("INSERT INTO nodes(name, incoming_sites, outgoing_sites)	VALUES(?,?,?)", (targeted_sites[iterator], 1, 0))
			else:
				incoming_sites = found[0] + 1
				cursor.execute("UPDATE nodes SET incoming_sites=? WHERE name=?", (incoming_sites, targeted_sites[iterator],))
		cursor.execute("SELECT id FROM nodes WHERE name=?", (name,))
		source_id_aux = cursor.fetchone()
		source_id = source_id_aux[0]
		for iterator in range(len(targeted_sites)):
			cursor.execute("SELECT id FROM nodes WHERE name=?", (targeted_sites[iterator],))
			target_id_aux = cursor.fetchone()
			target_id = target_id_aux[0]
			cursor.execute("INSERT INTO links(source, target) VALUES(?,?)", (source_id, target_id))
		connection.commit() # commit the change(s)
	except sqlite3.DatabaseError as e:
		logging.error("Something was wrong with the Database")
		connection.rollback() # roll back any change if something goes wrong
		raise e
	finally:
		connection.close() # close the db connection

def set_degree(num):
	'''
	EN: It assings a certain degree to a site depending on the sites that point at it.
	SP: Asigna un determinado grado a un site en función de los sites que lo apuntan.
	
	:param num: number of sites that point to the site / número de sitios que apuntan al site
	:return: the assigned degree / el grado asignado
	'''
	if num >= 15:
		return 8
	elif num >= 12:
		return 7
	elif num >= 10:
		return 6
	elif num >= 8:
		return 5
	elif num >= 6:
		return 4
	elif num >= 4:
		return 3
	elif num >= 2:
		return 2
	else:
		return 1

def update_degree_to_database():
	'''
	EN: It updates the degree value for each site in the database.
	SP: Actualiza el valor de degree para cada site en la base de datos.
	'''
	logging.debug("Dentro de set_degree()")
	try:
		connection = sqlite3.connect("C:\Program Files (x86)\Ampps\www\i2p_database.db") # open the db
		cursor = connection.cursor() # get a cursor object
		cursor.execute("SELECT id, incoming_sites, name FROM nodes")
		result = cursor.fetchall()
		for i in range(len(result)):
			node_id = result[i][0]
			incoming_sites = result[i][1]
			name = result[i][2]
			degree = set_degree(incoming_sites)
			logging.debug("DEGREE = " + str(degree) + " assigned to " + str(name))
			cursor.execute("UPDATE nodes SET degree=? WHERE id=?", (degree, node_id,))
		connection.commit() # commit the change(s)
	except sqlite3.DatabaseError as e:
		logging.error("Something was wrong with the Database")
		connection.rollback() # roll back any change if something goes wrong
		raise e
	finally:
		connection.close() # close the db connection

def update_top():
	'''
	EN: It updates the TOP tables of sites with more incoming_sites (Table Incoming_Top) and with more outgoing_sites (Table Outgoing_Top).
	SP: Actualiza las tablas de los TOP de sites con más incoming_sites (Tabla Incoming_Top) y con más outgoing_sites (Tabla Outgoing_Top).
	'''
	logging.debug("Dentro de update_top()")
	try:
		connection = sqlite3.connect("C:\Program Files (x86)\Ampps\www\i2p_database.db") # open the db
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

def db_to_json():
	'''
	EN: It generates a file in json format with the nodes and links that are contained in the database.
	SP: Genera un archivo en formato json con los nodos y links contenidos en la base de datos.
	'''
	logging.debug("Dentro de db_to_json()")
	connection = sqlite3.connect("C:\Program Files (x86)\Ampps\www\i2p_database.db")
	connection.row_factory = dict_factory
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM nodes ORDER BY id")
	nodes = cursor.fetchall()
	cursor.execute("SELECT * FROM links ORDER BY source")
	links = cursor.fetchall()
	json_result = json.dumps({"nodes": nodes, "links": links}, sort_keys=True, indent=4, separators=(',', ': '))
	with open('C:\Program Files (x86)\Ampps\www\i2p_data.json', 'wb') as f:
		f.write(json_result)

seed_sites = [
	"auchan.i2p",
	"city.i2p",
	"mochimochi.i2p",
	"wa11ed.city.i2p",
	"102chan.i2p", 
	"1st.i2p", 
	"333.i2p", 
	"alice.i2p",
	"andmp.i2p", 
	"animal.i2p",
	"anodex.i2p",
	"anongw.i2p",
	"anoncoin.i2p",
	"aosp.i2p",
	"arc2.i2p",
	"archaicbinarybbs.i2p",
	"archiv.tutorials.i2p",
	"backup.i2p",
	"bigbrother.i2p",
	"bitlox.i2p",
	"black.i2p",
	"blog.tinlans.i2p",
	"bmw.i2p", 
	"bmworc.i2p",
	"bobthebuilder.i2p",
	"boerse.i2p",
	"bofh.i2p",
	"bote.i2p",
	"cathugger.i2p",
	"cerapadus.i2p",
	"check.kovri.i2p",
	"chess.i2p",
	"chitanka.i2p",
	"ciphercraft.i2p",
	"co.i2p",
	"crypthost.i2p",
	"darkrealm.i2p",
	"darrob.i2p",
	"dead.i2p",
	"deb-mirror.i2p",
	"deepwebradio.i2p",
	"def2.i2p",
	"def3.i2p",
	"def4.i2p",
	"det.i2p",
	"diasporg.i2p",
	"diftracker.i2p",
	"dumpteam.i2p",
	"echelon.i2p",
	"epub-eepsite.i2p",
	"exch.i2p",
	"exchange.gostcoin.i2p",
	"exchanged.i2p",
	"explorer.gostcoin.i2p",
	"fa.i2p",
	"fantasy-worlds.i2p",
	"fido.r4sas.i2p", 
	"flibusta.i2p",
	"forum.rus.i2p",
	"forums.i2p",
	"freedomforum.i2p",
	"freefallheavens.i2p",
	"fs.i2p",
	"fsoc.i2p",
	"ginnegappen.i2p",
	"git.crypthost.i2p",
	"git.psi.i2p",
	"git.repo.i2p",
	"go.i2p",
	"h13.i2p",
	"hackerculture.i2p",
	"hagen.i2p",
	"heisenberg.i2p",
	"hiddenbooru.i2p",
	"hiddenchan.i2p",
	"hq.postman.i2p",
	"i2p-epub-eepsite.i2p",
	"i2p-scene.i2p",
	"i2pbuggenie.i2p",
	"i2pd.i2p",
	"i2p-projekt.i2p",
	"i2pdarknetmap.i2p",
	"i2pdocs.str4d.i2p",
	"i2pforum.i2p",
	"i2pjump.i2p",
	"i2pnews.i2p",
	"i2podisy.i2p",
	"i2push.i2p", 
	"i2pwiki.i2p",
	"identiguy.i2p",
	"ilcosmista.i2p",
	"ilita.i2p",
	"in.i2p",
	"inclib.i2p",
	"infosecurity.i2p",
	"infoserver.i2p",
	"inr.i2p",
	"irc.r4sas.i2p",
	"isotoxin.i2p",
	"ivorytower.i2p",
	"jikx.i2p",
	"k1773r.i2p", 
	"kellett.i2p",
	"keys.echelon.i2p",
	"kycklingar.i2p",
	"libertor.i2p",
	"lifebox.i2p",
	"lm.i2p",
	"lodikon.i2p",
	"lolicatgirls.i2p",
	"lolifox.i2p",
	"magix.i2p",
	"magnets.i2p",
	"marlin23732.i2p",
	"me.i2p",
	"meeh.i2p",
	"monero-build.i2p",
	"mosbot.i2p",
	"mosfet.i2p",
	"mrbamboo.i2p",
	"mysterious.i2p",
	"mystery.i2p",
	"nastycomics.i2p",
	"neodome.i2p",
	"no.i2p",
	"normal.i2p",
	"novospice.i2p",
	"nvspc.i2p",
	"obscuratus.i2p",
	"ol.i2p",
	"onelon.i2p",
	"onhax.i2p",
	"oniichan.i2p",
	"opendiftracker.i2p",
	"opentracker.dg2.i2p",
	"opsec.i2p",
	"orc.i2p",
	"overchan.oniichan.i2p",
	"papel.i2p",
	"passwd.i2p",
	"pasta-nojs.i2p",
	"paste.crypthost.i2p",
	"paste.r4sas.i2p",
	"pisekot.i2p",
	"pizdabol.i2p",
	"planet.i2p",
	"pomoyka.i2p",
	"pool.gostcoin.i2p",
	"pravtor.i2p",
	"project-future.i2p",
	"projectmayhem2012-086.i2p",
	"psi.i2p",
	"psy.i2p",
	"ptt.i2p",
	"publicwww.i2p",
	"r4sas.i2p",
	"rebel.i2p",
	"redzara.i2p",
	"reg.rus.i2p",
	"repo.i2p",
	"repo.r4sas.i2p",
	"reseed.i2p",
	"rideronthestorm.i2p",
	"rpi.i2p",
	"ru.i2p",
	"rufurus.i2p",
	"rus.i2p",
	"ruslibgen.i2p",
	"rust.i2p",
	"rutor.i2p",
	"secure.thetinhat.i2p",
	"seeker.i2p",
	"serien.i2p",
	"shoronil.i2p",
	"skank.i2p",
	"stats.i2p",
	"status.str4d.i2p",
	"str4d.i2p",
	"stream.i2p",
	"suicidal.i2p",
	"syndie-project.i2p",
	"tabak.i2p",
	"thebland.i2p",
	"thisthingimade.i2p",
	"thornworld.i2p",
	"thoughtfoundryblog.i2p",
	"torrentfinder.i2p",
	"torrfreedom.i2p",
	"trac.i2p2.i2p",
	"tracker.crypthost.i2p",
	"tracker.lodikon.i2p",
	"tracker.thebland.i2p",
	"tracker2.postman.i2p",
	"traditio.i2p",
	"ts.i2p",
	"tutorials.i2p",
	"unqueued.i2p",
	"visibility.i2p",
	"w.i2p",
	"wallet.gostcoin.i2p",
	"wiki.ilita.i2p",
	"infoserver.i2p",
	"xc.i2p",
	"xotc.i2p",
	"zab.i2p",
	"zerobin.i2p",
	"zzz.i2p",
]
ignored_sites = []
visited_sites = []
ongoing_sites = []
pending_sites = []
pending_sites = copy.deepcopy(seed_sites)
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
	global ignored_sites
	global pending_sites
	global visited_sites
	global ongoing_sites
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
			update_degree_to_database()
			update_top()
			db_to_json()
			results()

if __name__ == '__main__':
    main()
