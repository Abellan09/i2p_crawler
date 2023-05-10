# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Darknet_spider_state(scrapy.Item):

	'''
	EN: Item that represents the state of the spider.
	SP: Item que representa el estado del spider.
	'''

	darksite = scrapy.Field()
	visited_links = scrapy.Field()
	language = scrapy.Field()
	extracted_darksites = scrapy.Field()
	total_darksite_pages = scrapy.Field()
	title = scrapy.Field()
	size_main_page = scrapy.Field()
	main_page_tokenized_words = scrapy.Field()
