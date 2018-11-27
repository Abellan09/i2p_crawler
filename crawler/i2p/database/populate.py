# -*- coding: utf-8 -*-

"""
    :mod:`populate`
    ===========================================================================
    :synopsis: populates database tables and adds default info
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

from pony.orm import *
import dbutils

sql_debug(True)

# Populates the database tables and adds default info
with db_session:
    dbutils.add_default_info()