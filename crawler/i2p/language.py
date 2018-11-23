import subprocess	# https://docs.python.org/2/library/subprocess.html
import time			# https://docs.python.org/2/library/time.html
import os			# https://docs.python.org/2/library/os.html
import shutil		# https://docs.python.org/2/library/shutil.html
import json			# https://docs.python.org/2/library/json.html

def check():
	'''
	EN: It checks if in the /finished directory there are ".fail" and/or ".ok" files to process.
	SP: Comprueba si en el directorio /finished hay ficheros ".fail" y/o ".ok" que procesar.
	
	It adds the names of the ".ok" and ".fail" files to the ok_files and fail_files lists, respectively.
	After that, it calls the process() function.
	Añade los nombres de los ficheros ".ok" y ".fail" a las listas ok_files y fail_files, respectivamente.
	A continuación, llama a la función process().
	'''
	print("Dentro de check")
	global ok_files
	global fail_files
	finished_files = os.listdir("i2p/spiders/finished")
	#print ("FINISHED FILES: " + str(finished_files))
	for fil in finished_files:
		if (fil.endswith(".ok")) and (fil not in ok_files):
			ok_files.append(fil)
		if (fil.endswith(".fail")) and (fil not in fail_files):
			fail_files.append(fil)
	process()

def process():
	'''
	EN: It processes the files with ".ok" and ".fail" extension.
	SP: Procesa los ficheros con extensión ".ok" y ".fail".
	
	It moves the ".json" files of the sites that have been crawled correctly (.ok) from the /ongoing directory to the /finished
	and the /saved directory, opens said ".json" files in order to save the extracted language and deletes the ".ok" files once processed.
	Also, it deletes the files with the ".fail" extension from the /finished directory
	Mueve los ficheros ".json" de los sites que han sido crawleados correctamente (.ok) del directorio /ongoing	al directorio
	/finished y al directorio /saved, abre dichos ficheros ".json" para guardar el lenguaje extraído y borra los ficheros ".ok" una vez procesados.
	También, elimina los ficheros con extensión ".fail" del directorio /finished.
	'''
	print("Dentro de process")
	global ok_files
	global fail_files
	global visited_sites
	global pending_sites
	global ongoing_sites
	global dic_language
	global ongoing_crawlers
	files_to_remove_ok = []
	files_to_remove_fail = []
	if (ok_files or fail_files):
		try:
			for fil in ok_files:
				files_to_remove_ok.append(fil)
				fil_without_extension = fil.replace(".ok", "")
				fil_json_extension = fil.replace(".ok", ".json")
				source = "i2p/spiders/ongoing/" + fil_json_extension
				target = "i2p/spiders/finished/" + fil_json_extension
				target2 = "i2p/spiders/saved/" + fil_json_extension
				shutil.copy(source, target2)
				shutil.move(source, target)
				ongoing_sites.remove(fil_without_extension)
				with open(target) as f:
					crawled_items = json.load(f)
					language = crawled_items[len(crawled_items) - 1]["language"]
					eepsite = crawled_items[len(crawled_items) - 1]["eepsite"]
					dic_language[eepsite]=language
				if fil_without_extension not in visited_sites:
					visited_sites.append(fil_without_extension)
				eliminar = "i2p/spiders/finished/" + fil
				os.remove(eliminar)
				ongoing_crawlers -= 1
			for fil in fail_files:
				files_to_remove_fail.append(fil)
				eliminar = "i2p/spiders/finished/" + fil
				os.remove(eliminar)
				ongoing_crawlers -= 1
		except:
			print("There has been some error with the files")
		finally:
			for i in files_to_remove_ok:
				ok_files.remove(i)
			for j in files_to_remove_fail:
				fail_files.remove(j)

ok_files=[]
fail_files=[]
pending_sites=[]
ongoing_sites=[]
visited_sites=[]
dic_language={}
ongoing_crawlers=0

f = open("extracted_eepsites.txt")
line = f.readline()
while line != "":
	line = line.replace("\n", "")
	line = line.replace("\r", "")
	pending_sites.append(line)
	line = f.readline()
f.close()

while pending_sites or ongoing_sites:
	#print("Dentro de while")
	#print ongoing_crawlers
	if(ongoing_crawlers<30):
		#print("Dentro de if")
		next_site = pending_sites.pop()
		ongoing_sites.append(next_site)
		param1 = "url=http://" + next_site
		param2 = "i2p/spiders/ongoing/" + next_site + ".json"
		subprocess.Popen(["scrapy", "crawl", "i2p_main_page", "-a", param1, "-o", param2 ], shell=False)
		ongoing_crawlers += 1
	time.sleep(1) 
	check()

print("Crawling finished")
with open('language_result.json', 'w') as fil:
	json.dump(dic_language, fil)
	
