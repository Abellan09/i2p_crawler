# encoding: utf-8

import scrapy		# https://doc.scrapy.org/en/latest
import shutil		# https://docs.python.org/2/library/shutil.html
import urlparse		# https://docs.python.org/2/library/urlparse.html
import time			# https://docs.python.org/2/library/time.html
import json			# https://docs.python.org/2/library/json.html
import nltk			# https://www.nltk.org
from py_translator import Translator
from i2p.items import LanguageItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError 
from twisted.internet.error import TimeoutError, TCPTimedOutError

class I2P_Spider(scrapy.Spider):
	
	'''
	EN: Spider that is responsible for extracting the language in which the page is written.
	SP: Spider que se encarga de extraer el lenguaje en que está escrita la página a crawlear.
	
	For general information about scrapy.Spider, see: https://doc.scrapy.org/en/latest/topics/spiders.html
	Para obtener información general sobre scrapy.Spider, consulte: https://doc.scrapy.org/en/latest/topics/spiders.html
	'''
	
	name = "i2p_main_page"
	custom_settings = {
		'BOT_NAME': 'i2p_main_page',
	}
	end_time = 0
	start_time = 0
	start_urls = []
	error = True
	parse_eepsite = None
	item = LanguageItem()
	item["language"] = []
	languages = ["spanish","english","dutch","finnish","german","italian","portuguese","turkish","danish","french","hungarian","norwegian","russian","swedish"] # Lista de idiomas disponibles en la nltk
	LANGUAGES = {}
	
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
			with open("i2p/spiders/languages.json") as f:
				self.LANGUAGES = json.load(f)
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
				
		It stores the extracted data from each response in the corresponding Item.
		Almacena en el Item correspondiente los datos extraídos de cada response.
		
		:param response: response returned by an eepsite / respuesta devuelta por un eepsite.
		'''
		self.logger.debug("Dentro de parse()")
		self.error = False
		self.logger.info("Recieved response from {}".format(response.url))
		
		source_url = urlparse.urlparse(response.url)
		self.item["eepsite"] = source_url.netloc
		
		title = response.xpath('normalize-space(//title/text())').extract()
		self.item["title"] = title
		
		paragraphs = response.xpath('normalize-space(//p)').extract()
		h1 = response.xpath('//h1/text()').extract()
		h2 = response.xpath('//h2/text()').extract()
		h3 = response.xpath('//h3/text()').extract()
		h4 = response.xpath('//h4/text()').extract()

		#print paragraphs
		#print h1
		#print h2
		#print h3
		#print h4
		
		sample = title + paragraphs + h1 + h2 + h3 + h4
		sample = ' '.join(sample)
		if len(sample)>500:
			sample = sample[0:500]
		self.item["sample"] = sample
		
		# Con API de GOOGLE:
		translator = Translator()
		det = translator.detect(sample)
		language_google = self.LANGUAGES[det.lang]
		
		# Con nltk:
		# Dividimos el texto de entrada en tokens o palabras únicas
		tokens = nltk.tokenize.word_tokenize(sample)
		tokens = [t.strip().lower() for t in tokens] # Convierte todos los textos a minúsculas para su posterior comparación
		# Creamos un dict donde almacenaremos la cuenta de las stopwords para cada idioma
		lang_count = {}
		# Por cada idioma
		try:
			for lang in self.languages:
				# Obtenemos las stopwords del idioma del módulo nltk
				stop_words = unicode(nltk.corpus.stopwords.words(lang))
				lang_count[lang] = 0 # Inicializa a 0 el contador para cada idioma
				# Recorremos las palabras del texto a analizar
				for word in tokens:
					if word in stop_words: # Si la palabra se encuentra entre las stopwords, incrementa el contador
						lang_count[lang] += 1
			#print lang_count
			# Obtiene el idioma con el número mayor de coincidencias
			language_nltk = max(lang_count, key=lang_count.get)
			if lang_count[language_nltk] == 0:
				language_nltk = 'undefined'
		except UnicodeDecodeError as e:
			print 'Error'
			language_nltk = 'error'
		finally:
			print language_nltk
			print "Language detected!"
			
		self.item["language"].append(language_google)
		self.item["language"].append(language_nltk)
		
		self.end_time = time.time()
		self.item["time"] = str(self.end_time - self.start_time)
		yield self.item
	
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
		ok = ("./i2p/spiders/finished/" + site + ".ok")
		fail = ("./i2p/spiders/finished/" + site + ".fail")
		if self.error:
			f = open(fail, "w")
			f.close()
			self.logger.info(site + ".fail has been created at /i2p/spiders/finished")
		else:
			f = open(ok, "w")
			f.close()
			self.logger.info(site + ".ok has been created at /i2p/spiders/finished")
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
