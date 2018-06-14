# encoding: utf-8

import scrapy
import json
import urlparse
import shutil
import os
from i2p.items import I2PItem, I2PItemFinal
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError 
from twisted.internet.error import TimeoutError, TCPTimedOutError

class I2P_Spider(scrapy.Spider):
	
	name = "i2p"
	start_urls = []
	aux = I2PItem()
	item = I2PItemFinal()
	item["extracted_eepsites"]=[]
	visited_links = []
	parse_eepsite = None
	error = True
	extractor_i2p = LinkExtractor(tags=('a','area','base','link','audio','embed','iframe','img','input','script','source','track','video'),attrs=('href','src','srcset'),deny_domains=('net','com','info','org'),deny_extensions=())
	# extractor_multimedia = LinkExtractor(tags=('audio','embed','iframe','img','input','script','source','track','video'),attrs=('src','srcset'))
	# extractor_links = LinkExtractor(tags=('a','area','base','link'),attrs=('href'))
	
	def __init__(self, url=None, *args, **kwargs):
		super(I2P_Spider, self).__init__(*args, **kwargs)
		if url is not None:
			self.start_urls.append(url)
			self.parse_eepsite = urlparse.urlparse(url)
			#print self.parse_eepsite
		else:
			self.logger.error("No URL passed to crawl")
	
	def start_requests(self):
		for u in self.start_urls:
			yield scrapy.Request(u, callback = self.parse, errback = self.err, dont_filter=True)  
	
	def parse(self, response):
		self.error = False
		self.logger.info("Recieved response from {}".format(response.url))
		self.visited_links.append(response.url)
		self.aux["source_url"] = response.url
		source_url = urlparse.urlparse(response.url)
		self.aux["source_site"] = source_url.netloc
		links = self.extract_links(response)
		urls_list = []
		for link in links:
			urls_list.append(link.url)
			parse_link = urlparse.urlparse(link.url)
			if (parse_link.netloc not in self.item["extracted_eepsites"]) and (parse_link.netloc != self.parse_eepsite.netloc):
				self.item["extracted_eepsites"].append(parse_link.netloc)
			if (link.url not in self.visited_links) and (self.parse_eepsite.netloc == parse_link.netloc):
				yield scrapy.Request (link.url, callback = self.parse, errback = self.err, dont_filter=True)
		self.aux["list_of_urls"] = urls_list
		yield self.aux
		yield self.item
		
		# self.logger.info("List of URLs extracted from {}:".format(response.url))
		# print self.aux["list_of_urls"]
		# self.aux["url"]=response.xpath("//@href").extract()
		# filename = "list_of_urls_from_%s.json" % source_url.netloc
		# with open(filename, 'wb') as f:
			# f.write(str(self.aux["list_of_urls"]))
			# f.write(json.dumps(self.aux["list_of_urls"]))
		# self.log('Saved file %s' % filename)
		# return self.aux
	
	def extract_links(self, response):
		links = self.extractor_i2p.extract_links(response)
		return links
	
	def closed (self, reason):
		print ("DEBUG - Dentro de closed()")
		print ("SPIDER FINALIZADO")
		print ("ERROR = " + str(self.error))
		site = self.parse_eepsite.netloc
		#source = "./i2p/spiders/ongoing/" + site + ".json"
		ok = "./i2p/spiders/finished/" + site + ".ok"
		fail = "./i2p/spiders/finished/" + site + ".fail"
		# self.error = False
		if self.error:
			f = open(fail, "w")
			f.close()
			#shutil.move(source, fail)
			#shutil.copy(source, fail)
		else:
			f = open(ok, "w")
			f.close()
			#shutil.move(source, target)
			#shutil.copy(source, ok)
		
	def err(self, failure):
		# logs failures
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
