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
import threading
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

    def __init__(self, max_tries, duration, max_single_threads):
        super(DiscoveringThread, self).__init__()
        self._sites_to_discover = []
        self._max_tries = max_tries
        self._duration = duration
        self._max_single_threads = max_single_threads

    def run(self):

        # Doing until stop request
        while not self._stopped_event.isSet():

            with db_session:
                # Restoring the crawling status
                status = siteutils.get_crawling_status()
                # restored discovering sites
                self._sites_to_discover = status[dbsettings.Status.DISCOVERING.name]
                logging.debug("Current # of sites to discover %s.", self._sites_to_discover)

            # Running Threads
            simple_threads = []
            running_threads = 0

            # While there sites to discover and running threads
            while self._sites_to_discover or running_threads != 0:

                # How many simultaneous single threads are allowed to be running?
                while (self._max_single_threads - running_threads) > 0:
                    if self._sites_to_discover:
                        eepsite = self._sites_to_discover.pop()
                        ssdThread = SingleSiteDiscoveryThread(self._max_tries, self._duration, eepsite)
                        ssdThread.setName("SingleSiteDiscoveryThread_"+str(eepsite))
                        ssdThread.start()
                        logging.debug("Running threads counter: %s",running_threads)
                        simple_threads.insert(running_threads, ssdThread)
                        #logging.debug("Simple threads: %s", [t.getName() if t is not None else None for t in simple_threads])
                        running_threads += 1
                        logging.debug("Running %s", ssdThread.getName())
                    else:
                        break

                # Checking running threads
                for i, thread in enumerate(simple_threads):
                    if thread is not None:
                        logging.debug("SingleSiteDiscoveryThread %s is alive? %s", thread.name, thread.isAlive())
                        if not thread.isAlive():
                            simple_threads[i] = None
                            running_threads -= 1

                logging.debug("%s SingleSiteDiscoveryThread are running", running_threads)

                time.sleep(1)

            time.sleep(1)

    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        logging.debug("Stopping DiscoveryThread ...")


class SingleSiteDiscoveryThread(I2PThread, object):

    def __init__(self, max_tries, duration, eepsite):
        super(SingleSiteDiscoveryThread, self).__init__()
        self._max_tries = max_tries
        self._duration = duration
        self._eepsite = eepsite

    def run(self):

            try:
                with db_session:
                    # Get next site
                    # eepsite = self._sites_to_discover.pop()

                    logging.debug("Trying to discover site %s", self._eepsite)

                    # Computes the time spent from the first discovering status of the eepsite
                    time_spent = datetime.now() - \
                                 dbutils.get_processing_logs_by_site_status(s_url=self._eepsite,
                                                                            s_status=dbsettings.Status.DISCOVERING)[
                                     0].timestamp
                    discovering_tries = dbutils.get_site(s_url=self._eepsite).discovering_tries
                    logging.debug("Time spent for site %s: %s ", self._eepsite, time_spent)
                    logging.debug("Current tries for site %s: %s ", self._eepsite, discovering_tries)

                    # Checking maximum discovering tries and period of time for trying
                    if discovering_tries < self._max_tries \
                            and time_spent <= timedelta(minutes=self._duration):

                        eepsite_http = "http://" + self._eepsite
                        logging.debug("DISCOVERING: %s", self._eepsite)
                        response = request_conn.connectThroughProxy(eepsite_http,
                                                                    proxies={'http': 'http://localhost:4444'})
                        response_code = str(response.status_code)
                        response_time = str(response.elapsed.total_seconds())
                        # Print CSV Line
                        csv_line = ""
                        csv_line += self._eepsite + "|" + response_code + "|"
                        csv_line += response_time + "|" + str(discovering_tries)
                        logging.debug("RESPONSE: %s", csv_line)

                        logging.debug("Increasing discovering tries to site %s.", self._eepsite)
                        dbutils.increase_tries_on_discovering(s_url=self._eepsite)

                        # HTTP 2XX or 3XX
                        if reg_http.match(response_code):
                            dbutils.set_site_current_processing_status(s_url=self._eepsite,
                                                                       s_http_status=response_code,
                                                                       s_http_response_time=response_time,
                                                                       s_status=dbsettings.Status.PENDING)
                            logging.debug("Site %s was set up to PENDING.", self._eepsite)
                        # HTTP 4XX or 5XX
                        else:
                            dbutils.set_site_current_processing_status(s_url=self._eepsite,
                                                                       s_http_status=response_code,
                                                                       s_http_response_time=response_time,
                                                                       s_status=dbsettings.Status.DISCOVERING)
                            logging.debug("Site %s was set up to DISCOVERING the response code %s received.", self._eepsite, response_code)
                    else:
                        dbutils.set_site_current_processing_status(s_url=self._eepsite,
                                                                   s_status=dbsettings.Status.DISCARDED)
                        logging.debug("Site %s was set up to DISCARDED because tries were %s (max %s) or duration was %s (max %s mins).", self._eepsite, discovering_tries, self._max_tries, time_spent, self._duration)

            except Exception as e:
                logging.error("ERROR on discovering %s: %s", self._eepsite, e)
                logging.debug("Increasing discovering tries to site %s.", self._eepsite)
                with db_session:
                    dbutils.increase_tries_on_discovering(s_url=self._eepsite)

    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        logging.debug("Stopping SingleSiteDiscoveryThread for site %s ",self._eepsite )
