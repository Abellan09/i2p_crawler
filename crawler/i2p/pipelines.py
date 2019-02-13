# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import i2psettings

# Scrapped items
NO_VISITED = "non_visited_links"
VISITED = "visited_links"
EEPSITE = "eepsite"
LANGUAGE = "language"
EEPSITE_LINKS = "extracted_eepsites"

class I2PPipeline(object):
    """
    Scrapy Pipeline for overwriting the output JSON file, so just one line is stored at the end of the site crawling
    process
    """

    def open_spider(self, spider):
        self.file = open(i2psettings.PATH_ONGOING_SPIDERS + spider.state_item["eepsite"] + '.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        """
        Overwrites the json eepsite file, just keeping only one line.
        It is called to preprocess the scrapped items just before they are stored.

        :param item - The scrapped items
        :param spider: Spider - The instance of the launched spider.
        :return: item - The previously defined items
        """

        # Preprocessing just for keepping just the needed info.
        to_save = {}
        to_save[EEPSITE] = item[EEPSITE]
        to_save[LANGUAGE] = item[LANGUAGE]
        to_save[EEPSITE_LINKS] = item[EEPSITE_LINKS]

        line = json.dumps(dict(to_save)) + "\n"
        self.file.seek(0)
        self.file.write(line)
        return item
