# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy import exceptions
from database import connection_settings

class DarknetFilterMiddleware(object):
	
	'''
	EN: Middleware that is responsible for filtering extensions that are not going to be taken into account.
	SP: Middleware que se encarga de filtrar las extensiones que no se van a tener en cuenta.
	'''
	
	extensions = [
	# images
	".mng", ".pct", ".bmp", ".gif", ".jpg", ".jpeg", ".png", ".pst", ".psp", ".tif",
    ".tiff", ".ai", ".drw", ".dxf", ".eps", ".ps", ".svg", ".ico",
    # audio
    ".mp3", ".wma", ".ogg", ".wav", ".ra", ".aac", ".mid", ".au", ".aiff",
    # video
    ".3gp", ".asf", ".asx", ".avi", ".mov", ".mp4", ".mpg", ".qt", ".rm", ".swf", ".wmv",
    ".m4a", ".m4v", ".flv",
    # office suites
    ".xls", ".xlsx", ".ppt", ".pptx", ".pps", ".doc", ".docx", ".odt", ".ods", ".odg",
    ".odp", ".txt"
    # code
    ".cpp", ".java", ".class", ".jar", ".py", ".pyc", ".pyo", ".pyw", ".rb", ".rbw", ".pl", ".pm", ".cgi",
    # other
    ".css", ".pdf", ".exe", ".bin", ".rss", ".zip", ".rar", ".tar", ".gz", ".su3",
	]
	
	def process_request(self, request, spider):
		if(any(ext in request.url for ext in self.extensions)):
			raise exceptions.IgnoreRequest
		else:
			return None				


class DarknetProxyMiddleware(object):
	
	'''
	EN: Middleware that is responsible for defining the proxy so that requests are made to the network.
	SP: Middleware que se encarga de definir el proxy para que las peticiones se hagan a la red.
	'''	
	
	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s
	
	def process_request(self, request, spider):
		#request.meta['proxy'] = "http://127.0.0.1:8888"
		if not connection_settings.PROXY:
			request.meta['proxy'] = None
		else:
			request.meta['proxy'] = "http://"+connection_settings.PROXY
		
		return None
		# Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
	
	def process_response(self, request, response, spider):
		# Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
		return response
		
	def process_exception(self, request, exception, spider):
		# Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
		pass
		
	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)
