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
MAX_CRAWLING_TRIES_ON_DISCOVERING = 24*30  # 30 days, 1 try per hour
# Number of tries for error sites
MAX_DURATION_ON_DISCOVERING = 24*30*60  # Minutes --> 30 days
# Number of parallel single threads running
MAX_SINGLE_THREADS_ON_DISCOVERING = 50
# Http response timeout
HTTP_TIMEOUT = 30  # Seconds
# Initial seed file
INITIAL_SEEDS = "all_seeds.txt"
# Batch size of initial seeds
INITIAL_SEEDS_BACH_SIZE = 475  # 4750/10=475
# Time to wait until the next seeds self-assignment
SEEDS_ASSIGMENT_PERIOD = 30*60  # seconds
