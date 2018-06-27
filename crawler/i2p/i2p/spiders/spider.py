# encoding: utf-8

import scrapy		# https://doc.scrapy.org/en/latest
import shutil		# https://docs.python.org/2/library/shutil.html
import urlparse		# https://docs.python.org/2/library/urlparse.html
import time			# https://docs.python.org/2/library/time.html
from i2p.items import I2PItem, I2PItemFinal
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError 
from twisted.internet.error import TimeoutError, TCPTimedOutError

class I2P_Spider(scrapy.Spider):
	
	'''
	EN: Spider that is responsible for extracting the links contained in an eepsite.
	SP: Spider que se encarga de extraer los links contenidos en un eepsite.
	
	For general information about scrapy.Spider, see: https://doc.scrapy.org/en/latest/topics/spiders.html
	Para obtener información general sobre scrapy.Spider, consulte: https://doc.scrapy.org/en/latest/topics/spiders.html
	'''
	
	name = "i2p"
	end_time = 0
	start_time = 0
	start_urls = []
	visited_links = []
	parse_eepsite = None
	error = True
	aux = I2PItem()
	item = I2PItemFinal()
	item["extracted_eepsites"]=[]
	extractor_i2p = LinkExtractor(tags=('a','area','base','link','audio','embed','iframe','img','input','script','source','track','video'),attrs=('href','src','srcset'),deny_domains=('net','com','info','org'),deny_extensions=())
	# extractor_multimedia = LinkExtractor(tags=('audio','embed','iframe','img','input','script','source','track','video'),attrs=('src','srcset'),deny_domains=('net','com','info','org'),deny_extensions=())
	# extractor_links = LinkExtractor(tags=('a','area','base','link'),attrs=('href'),deny_domains=('net','com','info','org'),deny_extensions=())
	
	def __init__(self, url=None, *args, **kwargs):
		'''
		EN: It initializes the seed URL list with the URL that has been passed as a parameter
		SP: Inicializa la lista de URLs semilla con la URL pasada como parámetro.
		
		:param url: url of the site to crawl / url del site a crawlear
		'''
		super(I2P_Spider, self).__init__(*args, **kwargs)
		self.logger.debug("Dentro de __init__()")
		if url is not None:
			self.start_urls.append(url)
			self.parse_eepsite = urlparse.urlparse(url)
			self.start_time = time.time()
			self.logger.info("Start URL: %s", self.parse_eepsite)
		else:
			self.logger.error("No URL passed to crawl")
	
	def start_requests(self):
		'''
		EN: It returns an iterable of Requests which the Spider will begin to crawl.
		SP: Devuelve un iterable de Requests que el Spider comenzará a crawlear.
		'''
		self.logger.debug("Dentro de start_requests()")
		for u in self.start_urls:
			yield scrapy.Request(u, callback = self.parse, errback = self.err, dont_filter=True)  
	
	def parse(self, response):
		'''
		EN: It handles the downloaded response for each of the made requests.
		SP: Maneja la respuesta descargada para cada una de las solicitudes realizadas.
				
		It stores the extracted eepsites from each response in the corresponding Item.
		In addition, it makes a yield to itself with a Request for each of the internal links of the site (with what the whole site is crawled).
		Almacena en el Item correspondiente los eepsites extraídos de cada response.
		Además, hace un yield a sí mismo con una Request para cada uno de los enlaces internos del site (con lo que se crawlea el site entero).
		
		:param response: response returned by an eepsite / respuesta devuelta por un eepsite.
		'''
		self.logger.debug("Dentro de parse()")
		self.error = False
		self.logger.info("Recieved response from {}".format(response.url))
		self.visited_links.append(response.url)
		self.aux["source_url"] = response.url
		source_url = urlparse.urlparse(response.url)
		self.aux["source_site"] = source_url.netloc
		links = self.get_links(response)
		urls_list = []
		for link in links:
			urls_list.append(link.url)
			parse_link = urlparse.urlparse(link.url)
			if (parse_link.netloc not in self.item["extracted_eepsites"]) and (parse_link.netloc != self.parse_eepsite.netloc):
				self.item["extracted_eepsites"].append(parse_link.netloc)
			if (link.url not in self.visited_links) and (self.parse_eepsite.netloc == parse_link.netloc):
				self.visited_links.append(link.url)
				yield scrapy.Request (link.url, callback = self.parse, errback = self.err, dont_filter=True)
		self.aux["list_of_urls"] = urls_list
		yield self.aux
		yield self.item
	
	def get_links(self, response):
		'''
		EN: It extracts the links from a certain eepsite.
		SP: Extrae los links de un determinado eepsite.
		
		:param response: response returned by an eepsite / respuesta devuelta por un eepsite
		:return: list that contains the extracted links / lista que contiene los links extraídos
		'''
		self.logger.debug("Dentro de get_links()")
		links = self.extractor_i2p.extract_links(response)
		return links
	
	def closed (self, reason):
		'''
		EN: It is called when the spider has ended the crawling process.
		SP: Se llama cuando el spider ha terminado todo el proceso de crawling.
		
		It generates an empty file with ".fail" extension in case there has been any error and the site 
		hasn't been crawled correctly; otherwise, it generates an empty file with ".ok" extension.
		Genera un archivo vacío con extensión ".fail" en caso de que haya habido algún error y el site no 
		se haya podido crawlear correctamente; en caso contrario, genera un archivo vacío con extensión ".ok".
		
		:param reason: a string which describes the reason why the spider was closed / string que describre por qué ha finalizado el spider
		'''
		self.logger.debug("Dentro de closed()")
		self.logger.info("SPIDER FINALIZADO")
		self.logger.info("ERROR = " + str(self.error))
		site = self.parse_eepsite.netloc
		#source = "./i2p/spiders/ongoing/" + site + ".json"
		ok = "./i2p/spiders/finished/" + site + ".ok"
		fail = "./i2p/spiders/finished/" + site + ".fail"
		self.end_time = time.time()
		# self.error = False
		if self.error:
			f = open(fail, "w")
			f.close()
			self.logger.info(site + ".fail has been created at /i2p/spiders/finished")
			#shutil.move(source, fail)
			#shutil.copy(source, fail)
		else:
			f = open(ok, "w")
			f.close()
			self.logger.info(site + ".ok has been created at /i2p/spiders/finished")
			#shutil.move(source, target)
			#shutil.copy(source, ok)
			self.logger.info("Total time taken in crawling " + self.parse_eepsite.netloc + ": " + str(self.end_time - self.start_time) + " seconds.")
		
	def err(self, failure):
		'''
		EN: It reports about possible errors that may occur when a request fails.
		SP: Reporta los posibles errores que pueden producirse cuando una petición falla.
		
		This function is called when an error occurs (if any exception was raised while processing
		the request). The showed errors are: HttpError, DNSLookupError y TimeoutError.
		Esta función es llamada cuando ocurre un error (si se lanza cualquier extensión mientras se	procesa
		una respuesta). Son mostrados los errores: HttpError, DNSLookupError y TimeoutError.
		
		:param failure: type of error which has ocurred / tipo de error que ha ocurrido (https://twistedmatrix.com/documents/current/api/twisted.python.failure.Failure.html)
		'''
		self.logger.debug("Dentro de err()")
		self.error = True
		self.logger.error(repr(failure))  
		if failure.check(HttpError):
			response = failure.value.response 
			self.logger.error("HttpError occurred on %s", response.url)  
		elif failure.check(DNSLookupError): 
			request = failure.request 
			self.logger.error("DNSLookupError occurred on %s", request.url) 
		elif failure.check(TimeoutError, TCPTimedOutError): 
			request = failure.request 
			self.logger.error("TimeoutError occurred on %s", request.url) 
