# -*- coding: utf-8 -*-

"""
    :mod:`settings`
    ===========================================================================
    :synopsis: default data and constants for the database
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

from enum import Enum, unique

# Site status and type constants
# SITE STATUS

@unique
class Status(Enum):
    ONGOING = 1
    FINISHED = 2
    PENDING = 3
    ERROR = 4
    DISCARDED = 5
    DISCOVERING = 6
    ERROR_DEFUNC = 7


# {status:description}
SITE_STATUS_DEFAULT_INFO = {Status.ONGOING.name:'Ongoing: The site is being crawled',
                            Status.FINISHED.name:'Finished: The site has been successfully crawled',
                            Status.PENDING.name:'Pending: The site is waiting to be launched again. May there was a processing error.',
                            Status.ERROR.name:'Error: The site cannot be crawled',
                            Status.DISCARDED.name: 'Discarded: The site  has been discarded because the number of maximum tries or the temporal window is expired.',
                            Status.DISCOVERING.name: 'Discovering: The site is being discovered.',
                            Status.ERROR_DEFUNC.name: 'The spider subprocess has been stopped by the S.O.'}

# SITE TYPE
@unique
class Type(Enum):
    I2P = 1
    TOR = 2
    SURFACE = 3
    UNKNOWN = 4


#{type:description}
SITE_TYPE_DEFAULT_INFO = {Type.I2P.name:'I2P eepsite',
                          Type.TOR.name:'TOR onion site',
                          Type.SURFACE.name:'Surface web site',
                          Type.UNKNOWN.name:'Unknow site type'}

# To schedule the discovering time. Each site will be discover every TIME_INTERVAL_TO_DISCOVER
TIME_INTERVAL_TO_DISCOVER = 60  # minutes
