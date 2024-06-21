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
USERNAME = 'tor'

#DB password
PASSWORD = '1Uchn53d'

#DB name
DATABASE = 'tor'

#Proxy configuration (host:port or None)
#I2p
#PROXY = '127.0.0.1:4444'
#Freenet
#PROXY = None
#Tor - Through privoxy
PROXY = '127.0.0.1:8118'
