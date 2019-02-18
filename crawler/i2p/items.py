# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class I2P_spider_state(scrapy.Item):
	
	'''
	EN: Item that represents the state of the spider.
	SP: Item que representa el estado del spider.
	'''	
	
	eepsite = scrapy.Field()
	visited_links = scrapy.Field()
	non_visited_links = scrapy.Field()
	language = scrapy.Field()
	extracted_eepsites = scrapy.Field()
	total_eepsite_pages = scrapy.Field()
