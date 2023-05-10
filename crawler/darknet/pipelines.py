# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from darknet import darknetsettings

# Scrapped items
VISITED = "visited_links"
DARKSITE = "darksite"
LANGUAGE = "language"
DARKSITE_LINKS = "extracted_darksites"
TOTAL_PAGES = "total_darksite_pages"
TITLE = "title"
SIZE_MAIN_PAGE = "size_main_page"
TOKENIZED_WORDS = "main_page_tokenized_words"

class DarknetPipeline(object):
    """
    Scrapy Pipeline for overwriting the output JSON file, so just one line is stored at the end of the site crawling
    process
    """

    def open_spider(self, spider):
        self.file = open(darknetsettings.PATH_ONGOING_SPIDERS + spider.state_item["darksite"] + '.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        """
        Overwrites the json darksite file, just keeping only one line.
        It is called to preprocess the scrapped items just before they are stored.

        :param item - The scrapped items
        :param spider: Spider - The instance of the launched spider.
        :return: item - The previously defined items
        """

        # Preprocessing just for keepping just the needed info.
        to_save = {}
        to_save[DARKSITE] = item[DARKSITE]
        to_save[LANGUAGE] = item[LANGUAGE]
        to_save[DARKSITE_LINKS] = item[DARKSITE_LINKS]
        to_save[TOTAL_PAGES] = item[TOTAL_PAGES]
        to_save[TITLE] = item[TITLE]
        to_save[SIZE_MAIN_PAGE] = item[SIZE_MAIN_PAGE]
        to_save[VISITED] = item[VISITED]
        to_save[TOKENIZED_WORDS] = item[TOKENIZED_WORDS]

        line = json.dumps(dict(to_save)) + "\n"
        self.file.seek(0)
        self.file.write(line)
        return item
