# encoding: utf-8

import subprocess
import time
import urlparse
import copy
import os
import shutil
import sqlite3
import json

def results():
	print("RESULT - Total Launched Crawlers: " + str(total_crawlers))
	print("RESULT - Total Loop Executions: " + str(total_loop_executions))

#def trigger(param1, param2):
#	call(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2 ], shell=False)

def throw_crawler():
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
		#p = Process(target=trigger, args=(param1, param2,))
		#p.start()
		#p.join()
		#subprocess.Popen(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2 ], shell=False)
		subprocess.call(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2], shell=False)
		ongoing_crawlers += 1
		total_crawlers += 1

def check():
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
	print("DEBUG - Dentro de process_fail()")
	global fail_files
	global pending_sites
	files_to_remove = []
	print("DEBUG - Fail_files antes del bucle: " + str(fail_files))
	for fil in fail_files:
		eliminar = "i2p/spiders/finished/" + fil
		os.remove(eliminar)
		fil_without_extension = fil.replace(".fail", "")
		if fil_without_extension not in pending_sites:
			pending_sites.append(fil_without_extension)
			print("DEBUG - " + fil_without_extension + " add to pending_sites")
		files_to_remove.append(fil)
	#print ("Files to remove: " + str(files_to_remove))
	for i in files_to_remove:
		fail_files.remove(i)
	print("DEBUG - Fail_files despues del bucle: " + str(fail_files))
	
def process_ok():
	print("DEBUG - Dentro de process_ok()")
	global db_dictionary
	global ok_files
	global visited_sites
	global pending_sites
	global ongoing_sites
	global ongoing_crawlers
	files_to_remove = []
	print("DEBUG - ok_files antes del bucle: " + str(ok_files))
	for fil in ok_files:
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
			if (site not in pending_sites) and (site not in ongoing_sites) and (site not in visited_sites):
				pending_sites.append(site)
				#print site
				print("DEBUG - " + site + " add to pending_sites")
		files_to_remove.append(fil)
		eliminar = "i2p/spiders/finished/" + fil
		os.remove(eliminar)
	for i in files_to_remove:
		ok_files.remove(i)
	print("DEBUG - ok_files despues del bucle: " + str(ok_files))
		
def add_to_database():
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

def add_degree_to_nodes():
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

def set_degree(incoming_sites):
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
maximum_crawlers = 5
ongoing_crawlers = 0
total_crawlers = 0
total_loop_executions = 0
ok_files = []
fail_files = []
db_dictionary = {}

def main():
	global total_loop_executions
	global ongoing_crawlers
	global pending_sites
	global visited_sites
	global ongoing_sites
	while pending_sites or ongoing_sites:
		#print(time.strftime("DEBUG - Time: " + "%H:%M:%S", time.gmtime()))
		total_loop_executions += 1
		print("DEBUG - Pending sites: " + str(pending_sites))
		print("DEBUG - Finished sites: " + str(visited_sites))
		print("DEBUG - Ongoing sites: " + str(ongoing_sites))
		throw_crawler()
		print("INFO - Ongoing_crawlers: " + str(ongoing_crawlers))
		check()
		time.sleep(2) # duerme 2 segundos
	add_to_database()
	results()

if __name__ == '__main__':
    main()
