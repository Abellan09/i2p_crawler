import scrapy


class MyspiderSpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['myspider.com']
    start_urls = ['http://myspider.com/']

    def parse(self, response):
        pass
