# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json


class I2PPipeline(object):
    """
    Scrapy Pipeline for overwriting the output JSON file, so just one line is stored at the end of the site crawling
    process
    """

    def open_spider(self, spider):
        self.file = open('i2p/spiders/ongoing/' + spider.state_item["eepsite"] + '.json', 'w')

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
        line = json.dumps(dict(item)) + "\n"
        self.file.seek(0)
        self.file.write(line)
        return item
