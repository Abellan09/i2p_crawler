# -*- coding: utf-8 -*-

"""
    :mod:`connection_settings`
    ===========================================================================
    :synopsis: Settings about connection database and proxy
    :author: Emilio Figueras Martín
    :contact: emilio.figuerasmartin@alum.uca.es
    :organization: University of Cádiz
    :project: I2P Crawler
    :since: 0.0.1
"""

# Config db params
#Service of database
PROVIDER = 'mysql'

#DB host
HOST = '192.168.33.10'

#DB username
USERNAME = 'c4darknet'

#DB password
PASSWORD = '1Uchn53d'

#DB name
DATABASE = 'c4darknet'

#Proxy configuration (host:port or None)
# I2P = 127.0.0.1:4444
# FREENET = None
# TOR ='127.0.0.1:8118'
#PROXY = '127.0.0.1:4444'
#PROXY = None
PROXY = '127.0.0.1:8118'
