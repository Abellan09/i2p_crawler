# -*- coding: utf-8 -*-

"""
    :mod:`discoverythread`
    ===========================================================================
    :synopsis: Thread for checking eepsites availability
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

import logging
import time
from datetime import datetime
from datetime import timedelta

import regex
from database import dbutils, dbsettings, entities
from pony.orm import db_session
from utils import siteutils

from i2pthread import I2PThread
from qos import request_conn

# Set to True to show pony SQL queries
#set_sql_debug(debug=True)
# Regular expression for HTTP successful response codes
HTTP_SUCCES_COD_REGEXPR = '[23]'
reg_http = regex.compile(HTTP_SUCCES_COD_REGEXPR)

class DiscoveringThread(I2PThread, object):

    def __init__(self, max_tries, duration):
        super(DiscoveringThread, self).__init__()
        self._sites_to_discover = []
        self._max_tries = max_tries
        self._duration = duration

    def run(self):

        # Doing until stop request
        while not self._stopped_event.isSet():

            with db_session:
                # Restoring the crawling status
                status = siteutils.get_crawling_status()
                # restored discovering sites
                self._sites_to_discover = status[dbsettings.Status.DISCOVERING.name]
                logging.debug("Current # of sites to discover %s.", self._sites_to_discover)

                for eepsite in self._sites_to_discover:

                    with db_session:

                        try:
                            # Get next site
                            #eepsite = self._sites_to_discover.pop()

                            logging.debug("Trying to discover site %s",eepsite)

                            # Computes the time spent from the first discovering status of the eepsite
                            time_spent = datetime.now() - \
                                         dbutils.get_processing_logs_by_site_status(s_url=eepsite,
                                                                                    s_status=dbsettings.Status.DISCOVERING)[0].timestamp

                            logging.debug("Time spent for site %s: %s ", eepsite, time_spent)
                            logging.debug("Current tries for site %s: %s ", eepsite,
                                          dbutils.get_site(s_url=eepsite).discovering_tries)

                            # Checking maximum discovering tries and period of time for trying
                            if dbutils.get_site(s_url=eepsite).discovering_tries < self._max_tries \
                                    and time_spent <= timedelta(minutes=self._duration):

                                eepsite_http = "http://" + eepsite
                                logging.debug("DISCOVERING: %s", eepsite)
                                response = request_conn.connectThroughProxy(eepsite_http,
                                                                            proxies={'http': 'http://localhost:4444'})
                                response_code = str(response.status_code)
                                # Print CSV Line
                                csv_line = ""
                                csv_line += eepsite + "|" + response_code + "|"
                                csv_line += str(response.elapsed.total_seconds())
                                logging.debug("RESPONSE: %s", csv_line)

                                logging.debug("Increasing discovering tries to site %s.", eepsite)
                                dbutils.increase_tries_on_discovering(s_url=eepsite)

                                # HTTP 2XX or 3XX
                                if reg_http.match(response_code):
                                    dbutils.set_site_current_processing_status(s_url=eepsite,
                                                                               s_http_status=response_code,
                                                                               s_status=dbsettings.Status.PENDING)
                                    logging.debug("Site %s was set up to PENDING.", eepsite)
                                # HTTP 4XX or 5XX
                                else:
                                    dbutils.set_site_current_processing_status(s_url=eepsite,
                                                                               s_http_status=response_code,
                                                                               s_status=dbsettings.Status.DISCOVERING)
                                    logging.debug("Site %s was set up to DISCOVERING.", eepsite)
                            else:
                                dbutils.set_site_current_processing_status(s_url=eepsite,
                                                                           s_status=dbsettings.Status.DISCARDED)
                                logging.debug("Site %s was set up to DISCARDED.", eepsite)

                        except Exception as e:
                            logging.error("ERROR on discovering %s: %s", eepsite, e)
                            logging.debug("Increasing discovering tries to site %s.", eepsite)
                            dbutils.increase_tries_on_discovering(s_url=eepsite)

            time.sleep(1)

    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        print("Stopping DiscoveryThread ...")


class SimpleSiteDiscovery(I2PThread, object):
    pass
