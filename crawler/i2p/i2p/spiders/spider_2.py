# encoding: utf-8

import scrapy
import json
import urlparse
from i2p.items import I2PItem
import i2p.settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError 
from twisted.internet.error import TimeoutError, TCPTimedOutError

class I2P_Spider(scrapy.Spider):
	
	name = "i2p_2"
	start_urls = [
		#"http://i2pdarknetmap.i2p",
		#"http://identiguy.i2p",
		#"http://stats.i2p/cgi-bin/dashboard.cgi",
		"http://anoncoin.i2p",
		#"http://i2p-projekt.i2p/en",
		#"http://echelon.i2p",
		#"http://exchanged.i2p/en/home",
		#"http://zzz.i2p",
		#"http://planet.i2p",
		#"http://zerobin.i2p",
		#"http://i2pforum.i2p",
		#"http://secure.thetinhat.i2p",
		#"http://i2pwiki.i2p",
	]
	extractor_links = LinkExtractor(tags=('a','area','base','link'),attrs=('href'))
	# extractor_multimedia = LinkExtractor(tags=('audio','embed','iframe','img','input','script','source','track','video'),attrs=('src','srcset'), deny_extensions=())
	
	"""
	Si añado "deny_extensions()" dejando el interior del paréntesis vacío, no se ignora ninguna extensión.
	Si no lo pongo, se ignorarán las siguientes extensiones.
	
	IGNORED_EXTENSIONS = [
    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',

    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a', 'm4v', 'flv',

    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
    'odp',

    # other
    'css', 'pdf', 'exe', 'bin', 'rss', 'zip', 'rar',
	]
	"""	
	
	def start_requests(self):
		for u in self.start_urls:
			yield scrapy.Request(u, callback = self.parse, errback = self.err, dont_filter=True)  
	
	def parse(self, response):
		self.logger.info("Recieved response from {}".format(response.url))
		aux = I2PItem()
		aux["source_url"] = response.url
		source_url = urlparse.urlparse(response.url)
		links = self.extract_links(response)
		urls_list = []
		for link in links:
			urls_list.append(link.url)
		aux["list_of_urls"] = urls_list
		# self.logger.info("List of URLs extracted from {}:".format(response.url))
		# print aux["list_of_urls"]
		# aux["url"]=response.xpath("//@href").extract()
		# filename = "list_of_urls_from_%s.json" % source_url.netloc
		# with open(filename, 'wb') as f:
			# f.write(str(aux["list_of_urls"]))
			# f.write(json.dumps(aux["list_of_urls"]))
		# self.log('Saved file %s' % filename)
		return aux
		
	def extract_links(self, response):
		links = self.extractor_links.extract_links(response)
		return links
		
	def closed (self, reason):
		print ("\nSPIDER FINALIZADO")
	
	def err(self, failure):
		# logs failures
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
