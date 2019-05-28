# -*- coding: utf-8 -*-

"""
    :mod:`settings`
    ===========================================================================
    :synopsis: crawling process configuration parameters
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

# Config params
# Number of simultaneous spiders running
MAX_ONGOING_SPIDERS = 10
# Number of tries for error sites
MAX_CRAWLING_TRIES_ON_ERROR = 2
# Number of tries for error sites
MAX_CRAWLING_TRIES_ON_DISCOVERING = 5 # 1 week, 1 try per hour
# Number of tries for error sites
MAX_DURATION_ON_DISCOVERING = 2  # Minutes --> 1 week
# Number of parallel single threads running
MAX_SINGLE_THREADS_ON_DISCOVERING = 50
# Http response timeout
HTTP_TIMEOUT = 30  # Seconds
# Initial seeds
INITIAL_SEEDS = "seed_urls_200.txt"