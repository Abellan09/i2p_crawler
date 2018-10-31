# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class I2PItem(scrapy.Item):
	
	'''
	EN: Item that represents the partial results that you want to extract from each eepsite.
	SP: Item que representa los resultados parciales que se quieren extraer de cada eepsite.
	'''
	
	source_url = scrapy.Field()
	source_site = scrapy.Field()
	list_of_urls = scrapy.Field()

class I2PItemFinal(scrapy.Item):
	
	'''
	EN: Item that represents the final result that you want to extract from each eepsite: the eepsites that each eepsite points at.
	SP: Item que representa el resultado final que se quiere extraer de cada eepsite: los eepsites a los que apunta.
	'''
	
	extracted_eepsites = scrapy.Field()
