# -*- coding: utf-8 -*-

"""
    :mod:`request_conn`
    ===========================================================================
    :synopsis: HTTP requests and responses
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

import requests

def connectThroughProxy(eepsite_url, proxies):
    # headers
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'}
    response = requests.get(eepsite_url, proxies=proxies, headers=headers)
    return response
