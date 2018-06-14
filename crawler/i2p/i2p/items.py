# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class I2PItem(scrapy.Item):
    source_url = scrapy.Field()
    source_site = scrapy.Field()
    list_of_urls = scrapy.Field()

class I2PItemFinal(scrapy.Item):
	extracted_eepsites = scrapy.Field()
