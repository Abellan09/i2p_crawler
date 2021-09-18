# encoding: utf-8
'''
EN: Specific implementations of each spider for each darknet
SP: Implementaciones específicas de cada spider para cada darknet

For general information about scrapy.Spider, see: https://doc.scrapy.org/en/latest/topics/spiders.html
Para obtener información general sobre scrapy.Spider, consulte: https://doc.scrapy.org/en/latest/topics/spiders.html
'''

#import random 		# https://docs.python.org/2/library/random.html
import re			# https://docs.python.org/2.7/library/re.html
import logging
from logging.handlers import RotatingFileHandler
import sys
#import copy			# https://docs.python.org/2/library/copy.html
import time			# https://docs.python.org/2/library/time.html
#import operator		# https://docs.python.org/2/library/operator.html
import json			# https://docs.python.org/2/library/json.html
import os			# https://docs.python.org/2/library/os.html
import urllib.parse		# https://docs.python.org/2/library/urlparse.html
from database import dbsettings

from . import spiderBase


logger = logging.getLogger(__name__)
format = logging.Formatter('%(asctime)s %(levelname)s - %(threadName)s - mod: %(module)s, method: %(funcName)s, msg: %(message)s')

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

fh = RotatingFileHandler(spiderBase.darknetsettings.PATH_LOG + "spiders.log", maxBytes=0, backupCount=0) # NO rotation, neither by size, nor by number of files
fh.setFormatter(format)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


class I2P_Spider(spiderBase.spiderBase):

	'''
	EN: Spider that is responsible for extracting the links contained in an darksite.
	SP: Spider que se encarga de extraer los links contenidos en un darksite.

	For general information about scrapy.Spider, see: https://doc.scrapy.org/en/latest/topics/spiders.html
	Para obtener información general sobre scrapy.Spider, consulte: https://doc.scrapy.org/en/latest/topics/spiders.html
	'''

	name = dbsettings.Type.I2P.name

	def __init__(self, url=None, *args, **kwargs):
		'''
		EN: It initializes the seed URL list with the URL that has been passed as a parameter
		SP: Inicializa la lista de URLs semilla con la URL pasada como parámetro.

		:param url: url of the site to crawl / url del site a crawlear
		'''
		super(I2P_Spider, self).__init__(*args, **kwargs)
		logger.debug("Dentro de __init__()")
		self.extractor_darknet = spiderBase.LinkExtractor(tags=('a', 'area', 'base', 'link', 'audio', 'embed', 'iframe', 'img', 'input', 'script', 'source', 'track', 'video'),
		 						 attrs=('href', 'src', 'srcset'), allow_domains=('i2p'), deny_extensions=())
		if url is not None:
			with open(spiderBase.darknetsettings.PATH_DATA + "languages_google.json") as f:
				self.LANGUAGES_GOOGLE = json.load(f)
			with open(spiderBase.darknetsettings.PATH_DATA + "languages_nltk.txt") as g:
				line = g.readline()
				while line != "":
					line = line.replace("\n", "")
					self.LANGUAGES_NLTK.append(line)
					line = g.readline()

			logger.debug("URL inicial que se recibe = %s", url)
			self.parse_darksite = urllib.parse.urlparse(url)

			self.non_visited_links_filename = spiderBase.darknetsettings.PATH_ONGOING_SPIDERS + "nvl_" + self.parse_darksite.netloc + ".txt"
			if not os.path.isfile(self.non_visited_links_filename):
				f = open(self.non_visited_links_filename, "a")
				f.close()
				self.start_urls.append(url)
			elif os.stat(self.non_visited_links_filename).st_size != 0:
				max_size_start_urls = 50
				count = 0
				with open(self.non_visited_links_filename) as f:
					line = f.readline()
					while line != "" and count < max_size_start_urls:
						line = line.replace("\n", "")
						link = "http://" + str(self.parse_darksite.netloc) + line
						self.start_urls.append(link)
						logger.debug("Link añadido a start_urls: %s", str(link))
						count = count + 1
						line = f.readline()

			self.state_item["darksite"] = self.parse_darksite.netloc
			spider_file = spiderBase.darknetsettings.PATH_ONGOING_SPIDERS + self.state_item["darksite"] + ".json"
			ongoing_spider = os.path.exists(spider_file)
			if ongoing_spider:
				logger.debug("SPIDER YA LANZADO ANTERIORMENTE.")
				# Leemos la última línea y cargamos el estado.
				target = spider_file
				with open(target) as f:
					try:
						state = json.load(f)
						file_empty = False
					except ValueError as error:
						logger.debug("Invalid json: %s", error)
						file_empty = True
					if not file_empty:
						self.error = False
						if "visited_links" in state:
							self.state_item["visited_links"] = state["visited_links"]
							self.visited_links = self.state_item["visited_links"].copy()
						if "language" in state:
							self.state_item["language"] = state["language"]
						if "extracted_darksites" in state:
							self.state_item["extracted_darksites"] = state["extracted_darksites"]
						if "total_darksite_pages" in state:
							self.state_item["total_darksite_pages"] = state["total_darksite_pages"]
						if "title" in state:
							self.state_item["title"] = state["title"]
						if "size_main_page" in state:
							self.state_item["size_main_page"] = state["size_main_page"]
						if "main_page_tokenized_words" in state:
							self.state_item["main_page_tokenized_words"] = state["main_page_tokenized_words"]
						self.main_page = False
			else:
				self.start_urls.append(url)
				self.start_time = time.time()
				logger.info("Start URL: %s", str(self.start_urls[0]))
		else:
			logger.error("No URL passed to crawl")


class Freenet_Spider(spiderBase.spiderBase):
	'''
	EN: Spider that is responsible for extracting the links contained in an freesite.
	SP: Spider que se encarga de extraer los links contenidos en un darksite.

	For general information about scrapy.Spider, see: https://doc.scrapy.org/en/latest/topics/spiders.html
	Para obtener información general sobre scrapy.Spider, consulte: https://doc.scrapy.org/en/latest/topics/spiders.html
	'''

	name = dbsettings.Type.FREENET.name
	url = None
	url_parsed = None #URL Parsed to filename

	def __init__(self, url=None, *args, **kwargs):
		'''
		EN: It initializes the seed URL list with the URL that has been passed as a parameter
		SP: Inicializa la lista de URLs semilla con la URL pasada como parámetro.

		:param url: url of the site to crawl / url del site a crawlear
		'''
		super(Freenet_Spider, self).__init__(*args, **kwargs)
		logger.debug("Dentro de __init__()")


		self.extractor_darknet = spiderBase.LinkExtractor(tags=('a', 'area', 'base', 'link', 'audio', 'embed', 'iframe', 'img', 'input', 'script', 'source', 'track', 'video'),
								  attrs=('href', 'src', 'srcset'), allow_domains=['127.0.0.1:8888', 'localhost:8888'], process_value=self.process_value)
		if url is not None:
			with open(spiderBase.darknetsettings.PATH_DATA + "languages_google.json") as f:
				self.LANGUAGES_GOOGLE = json.load(f)
			with open(spiderBase.darknetsettings.PATH_DATA + "languages_nltk.txt") as g:
				line = g.readline()
				while line != "":
					line = line.replace("\n", "")
					self.LANGUAGES_NLTK.append(line)
					line = g.readline()

			logger.debug("URL inicial que se recibe = %s", url)

			self.parse_darksite = self.freenet_urlparse(url)
			self.url = self.parse_darksite.netloc
			self.url_parsed = self.url.replace('https://', '') #Freenet parsed
			self.url_parsed = self.url_parsed.replace('http://', '') #Freenet parsed
			self.url_parsed = self.url_parsed.replace('/', '__') #Freenet parsed
			self.url_parsed = self.url_parsed.replace('freenet:', '') #Deleted freenet: word

			#logger.debug("URL netloc parsed = {}".format(self.parse_darksite.netloc))

			self.non_visited_links_filename = spiderBase.darknetsettings.PATH_ONGOING_SPIDERS + "nvl_" + self.url_parsed + ".txt"
			if not os.path.isfile(self.non_visited_links_filename):
				f = open(self.non_visited_links_filename, "a")
				f.close()
				self.start_urls.append(url)
			elif os.stat(self.non_visited_links_filename).st_size != 0:
				max_size_start_urls = 50
				count = 0
				with open(self.non_visited_links_filename) as f:
					line = f.readline()
					while line != "" and count < max_size_start_urls:
						line = line.replace("\n", "")
						link = "http://" + str(self.parse_darksite.netloc) + line
						self.start_urls.append(link)
						logger.debug("Link añadido a start_urls: %s", str(link))
						count = count + 1
						line = f.readline()

			self.state_item["darksite"] = self.url_parsed
			spider_file = spiderBase.darknetsettings.PATH_ONGOING_SPIDERS + self.state_item["darksite"] + ".json"
			ongoing_spider = os.path.exists(spider_file)
			if ongoing_spider:
				logger.debug("SPIDER YA LANZADO ANTERIORMENTE.")
				# Leemos la última línea y cargamos el estado.
				target = spider_file
				with open(target) as f:
					try:
						state = json.load(f)
						file_empty = False
					except ValueError as error:
						logger.debug("Invalid json: %s", error)
						file_empty = True
					if not file_empty:
						self.error = False
						if "visited_links" in state:
							self.state_item["visited_links"] = state["visited_links"]
							self.visited_links = self.state_item["visited_links"].copy()
						if "language" in state:
							self.state_item["language"] = state["language"]
						if "extracted_darksites" in state:
							self.state_item["extracted_darksites"] = state["extracted_darksites"]
						if "total_darksite_pages" in state:
							self.state_item["total_darksite_pages"] = state["total_darksite_pages"]
						if "title" in state:
							self.state_item["title"] = state["title"]
						if "size_main_page" in state:
							self.state_item["size_main_page"] = state["size_main_page"]
						if "main_page_tokenized_words" in state:
							self.state_item["main_page_tokenized_words"] = state["main_page_tokenized_words"]
						self.main_page = False
			else:
				self.start_urls.append(url)
				self.start_time = time.time()
				logger.info("Start URL: %s", str(self.start_urls[0]))
		else:
			logger.error("No URL passed to crawl")

	def process_value(self, value):
		'''
		EN: Locate the Freesite within the analyzed data.
		SP: Localiza el Freesite dentro de los datos analizados.
		'''
		#logger.debug("Entra en process_value con el enlace: {}".format(value))
		FREENET_REGEX = r"""((((127.0.0.1|localhost):8888/){0,1}(freenet:){0,1}(USK|SSK)@[a-zA-Z0-9~\-]{43},[a-zA-Z0-9~\-]{43},(AQACAAE|AQABAAE|AQECAAE|AAMC--8|AAIC--8|AAICAAA)/[a-zA-Z0-9\-\._%?\\& ]{0,150})/?[0-9\-]{0,10})/?(.*)"""
		m = re.search(FREENET_REGEX, value)
		if m:
			#Nos aseguramos de que tenga el http en la direccion y eliminamos queries y fragments

			link = m.group(0).replace('http://', '')
			if "127.0.0.1" not in link and "localhost" not in link:
				link = '127.0.0.1:8888/' + link
			#logger.debug("Freesite localizado: {}".format(link))
			link_parse = self.freenet_urlparse(link)
			link = 'http://' + link_parse.netloc + link_parse.path
			return link

		#logger.debug("No se ha encontrado nada en: {}".format(value))
		return None

	#Clase utilizada para reflejar la descomposicion de un freesite
	class Freesite():
		'''
		EN: Auxiliary object for the decomposition of a freesite
		SP: Objeto auxiliar para la descomposicion de un freesite
		'''
		def __init__(self):
			self.scheme = ""
			self.netloc = ""
			self.path = ""
			self.params = ""
			self.query = ""
			self.fragment = ""

	def freenet_urlparse(self, url):
		'''
		EN: Break down a URL simulating the urlib function urlparse but for freenet addresses
		SP: Descompone una URL simulando la funcion urlparse de urllib pero para direcciones freenet

		:param url: Freesite url
		:return: The decomposition of the url / La descomposicion de la url
		'''

		parse_freesite = self.Freesite()

		#Agregamos el http si no lo tiene
		if url.find('http', 0, 4) == -1:
				url = 'http://' + url

		#Eliminamos la palabra freenet
		url = url.replace('freenet:', '')

		#Generamos el formato parsed simulando el urlparse de urllib para los freesites USK
		if url.find('USK@') != -1 or url.find('USK%40') != -1:
			url_split = url.split("/", 6)
			parse_freesite.scheme = ""
			parse_freesite.netloc = url_split[2] + "/" + url_split[3] + "/" + url_split[4] + "/" + url_split[5]
			if len(url_split) == 7:
				parse_freesite.path = "/" + url_split[6]
				if "?" in parse_freesite.path:
					path_split = parse_freesite.path.split("?", 1)
					parse_freesite.path = path_split[0]
					parse_freesite.query = "?" + path_split[1]
				else:
					parse_freesite.query = ""
				if "#" in parse_freesite.path:
					fragment_split = parse_freesite.path.split("#", 1)
					parse_freesite.path = fragment_split[0]
					parse_freesite.fragment = "#" + fragment_split[1]
				elif "#" in parse_freesite.query:
					fragment_split = parse_freesite.query.split("#", 1)
					parse_freesite.query = fragment_split[0]
					parse_freesite.fragment = "#" + fragment_split[1]
				else:
					parse_freesite.fragment = ""
				parse_freesite.params = ""
			else:
				parse_freesite.path = ""
				parse_freesite.params = ""
				parse_freesite.query = ""
				parse_freesite.fragment = ""
			#logger.debug("USK Parse freesite = {}".format(parse_freesite))
		#Generamos el formato parsed simulando el urlparse de urllib para los freesites CHK
		elif url.find('CHK@') != -1 or url.find('CHK%40') != -1:
			url_split = url.split("/", 2)
			parse_freesite.scheme = ""
			parse_freesite.netloc = url_split[2]
			parse_freesite.path = ""
			parse_freesite.params = ""
			parse_freesite.query = ""
			parse_freesite.fragment = ""
		#Generamos el formato parsed simulando el urlparse de urllib para los freesites SSK
		elif url.find('SSK@') != -1 or url.find('SSK%40') != -1:
			url_split = url.split("/", 5)
			parse_freesite.scheme = ""
			parse_freesite.netloc = url_split[2] + "/" + url_split[3] + "/" + url_split[4]
			if len(url_split) == 6:
				parse_freesite.path = "/" + url_split[5]
				if "?" in parse_freesite.path:
					path_split = parse_freesite.path.split("?", 1)
					parse_freesite.path = path_split[0]
					parse_freesite.query = "?" + path_split[1]
				else:
					parse_freesite.query = ""
				if "#" in parse_freesite.path:
					fragment_split = parse_freesite.path.split("#", 1)
					parse_freesite.path = fragment_split[0]
					parse_freesite.fragment = "#" + fragment_split[1]
				elif "#" in parse_freesite.query:
					fragment_split = parse_freesite.query.split("#", 1)
					parse_freesite.query = fragment_split[0]
					parse_freesite.fragment = "#" + fragment_split[1]
				else:
					parse_freesite.fragment = ""
				parse_freesite.params = ""
			else:
				parse_freesite.path = ""
				parse_freesite.params = ""
				parse_freesite.query = ""
				parse_freesite.fragment = ""
		#Generamos el formato parsed simulando el urlparse de urllib para los freesites KSK
		elif url.find('KSK@') != -1 or url.find('KSK%40') != -1:
			url_split = url.split("/", 2)
			parse_freesite.scheme = ""
			parse_freesite.netloc = url_split[2]
			parse_freesite.path = ""
			parse_freesite.params = ""
			parse_freesite.query = ""
			parse_freesite.fragment = ""
		#ERROR
		else:
			logger.error("ERROR: Freesite type not found - URL = %s", str(url))
			url_split = url.split("/", 2)
			parse_freesite.scheme = ""
			parse_freesite.netloc = url_split[2]
			parse_freesite.path = ""
			parse_freesite.params = ""
			parse_freesite.query = ""
			parse_freesite.fragment = ""

		return parse_freesite


	def delete_link_from_non_visited(self, link):
		'''
		EN: It deletes the link passed as parameter from the file that contains the non visited links.
		SP: Elimina el link pasado como parámetro del fichero que contiene los links no visitados.

		:param link: link to delete / link a eliminar
		'''
		#logger.debug("Dentro de delete_link_from_non_visited()")
		link_parse = self.freenet_urlparse(link)
		link_path = link_parse.path
		f = open(self.non_visited_links_filename, "r")
		lines = f.readlines()
		f.close()
		f = open(self.non_visited_links_filename, "w")
		for line in lines:
			if ((link_path not in line) and (not line.isspace())):
				#if (link_path not in line) and (line.isalnum()) and (not line.isspace()):
				line = line.replace("\n", "")
				line = line.replace(" ", "")
				f.write("\n")
				f.write(line)
		f.close()

	def check_link_in_non_visited(self, link):
		'''
		EN: It checks if the link passed as parameter is inside the file that contains the non visited links.
		SP: Comprueba si el link pasado como parámetro se encuentra dentro del archivo que contiene los links no visitados.

		:param link: link to check / link a comprobar
		:return: boolean that is True if the link is in the file; False otherwise / booleano que está a True si el link se encuentra en el fichero; a False en caso contrario
		'''
		#logger.debug("Dentro de check_link_in_non_visited()")
		link_parse = self.freenet_urlparse(link)
		link_path = link_parse.path
		belongs = False
		with open(self.non_visited_links_filename) as f:
			line = f.readline()
			while line != "" and not belongs:
				if link_path in line:
					belongs = True
				else:
					line = f.readline()
		return belongs

	def add_link_to_non_visited(self, link):
		'''
		EN: It adds the link passed as parameter to the file that contains the non visited links.
		SP: Añade el link pasado como parámetro al fichero que contiene los links no visitados.

		:param link: link to add / link a añadir
		'''
		logger.debug("Dentro de add_link_to_non_visited(): %s", str(link))
		link_parse = self.freenet_urlparse(link)
		link_path = link_parse.path
		f = open(self.non_visited_links_filename, "a+")
		f.write("\n")
		f.write(link_path)
		f.close()

	def parse(self, response):
		'''
		EN: It handles the downloaded response for each of the made requests.
		SP: Maneja la respuesta descargada para cada una de las solicitudes realizadas.

		It stores the extracted darksites from each response in the corresponding Item.
		In addition, it makes a yield to itself with a Request for each of the internal links of the site (with what the whole site is crawled).
		Almacena en el Item correspondiente los darksites extraídos de cada response.
		Además, hace un yield a sí mismo con una Request para cada uno de los enlaces internos del site (con lo que se crawlea el site entero).

		:param response: response returned by an darksite / respuesta devuelta por un darksite.
		'''

		try:
			self.error = False
			logger.debug("Received response from %s", str(response.url))
			if self.main_page:
				self.main_page_analysis(response)
				self.main_page = False
			self.add_visited_links(response.url)
			self.state_item["total_darksite_pages"] = len(self.visited_links)+self.overflow_visited_links
			if self.check_link_in_non_visited(response.url):
				self.delete_link_from_non_visited(response.url)
			self.state_item["visited_links"] = self.visited_links.copy()
			links = self.get_links(response)
			for link in links:
				parse_link = self.freenet_urlparse(link.url)
				#Comprobar que no sea un enlace interno
				if ((parse_link.netloc not in self.state_item["extracted_darksites"]) and (parse_link.netloc != self.parse_darksite.netloc)):
					self.state_item["extracted_darksites"].append(parse_link.netloc)
				#Si es un enlace interno y no ha sido visitado aun
				if ((not self.check_link_in_non_visited(link.url)) and (link.url not in self.visited_links) and (self.parse_darksite.netloc == parse_link.netloc)):
					self.add_link_to_non_visited(link.url)
					yield spiderBase.scrapy.Request(link.url, callback=self.parse, errback=self.err, dont_filter=True)
					if self.check_link_in_non_visited(response.url):
						self.delete_link_from_non_visited(response.url)
				yield self.state_item
			yield self.state_item
		except Exception as e:
			logger.error("ERROR scraping site %s: %s", response.url, e)
			raise

	def closed(self, reason):
		'''
		EN: It is called when the spider has ended the crawling process.
		SP: Se llama cuando el spider ha terminado todo el proceso de crawling.

		It generates an empty file with ".fail" extension in case there has been any error and the site
		hasn't been crawled correctly; otherwise, it generates an empty file with ".ok" extension.
		Genera un archivo vacío con extensión ".fail" en caso de que haya habido algún error y el site no
		se haya podido crawlear correctamente; en caso contrario, genera un archivo vacío con extensión ".ok".

		:param reason: a string which describes the reason why the spider was closed / string que describre por qué ha finalizado el spider
		'''
		logger.debug("Dentro de closed()")
		logger.info("SPIDER FINALIZADO")
		logger.info("ERROR = %s", str(self.error))
		#site = self.parse_darksite.netloc
		site = self.url_parsed

		logger.debug("SPIDER SITE = %s", site)
		ok = spiderBase.darknetsettings.PATH_FINISHED_SPIDERS + site + ".ok"
		fail = spiderBase.darknetsettings.PATH_FINISHED_SPIDERS + site + ".fail"
		target = spiderBase.darknetsettings.PATH_ONGOING_SPIDERS + site + ".json"
		self.end_time = time.time()
		if self.error:
			f = open(fail, "w")
			f.close()
			logger.debug(".fail has been created at %s", fail)
		else:
			f = open(ok, "w")
			f.close()
			logger.debug(".ok has been created at %s", ok)
			#logger.debug("Total time taken in crawling " + self.parse_darksite.netloc + ": " + str(self.end_time - self.start_time) + " seconds.")
			logger.debug("Total time taken in crawling %s: %s seconds.", self.url, str(self.end_time - self.start_time))
			if os.path.exists(self.non_visited_links_filename):
				os.remove(self.non_visited_links_filename)
			with open(target, 'r+') as f:
				data = json.load(f)
				del data["visited_links"]
				f.seek(0)
				json.dump(data, f)
				f.truncate()
