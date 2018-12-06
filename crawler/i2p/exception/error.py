# -*- coding: utf-8 -*-

"""
    :mod:`exception`
    ===========================================================================
    :synopsis: Error definitions
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""


class CrawlerError(Exception):
    """
    General crawler Error

    """
    pass

class DataBaseError(CrawlerError):
    """
    *Error definition related to the data sources modules/classes*

    See Also
    --------
    CrawlerError
    """
    def __init__(exc, msg, original_exc=None):
        Exception.__init__(exc, msg)
        exc.original_exc = original_exc