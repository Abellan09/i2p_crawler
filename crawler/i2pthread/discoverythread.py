# -*- coding: utf-8 -*-

"""
    :mod:`i2pthread`
    ===========================================================================
    :synopsis: I2P additional threads
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

import threading
from i2pthread import I2PThread

from qos import request_conn
from pony.orm import db_session
from ..database import dbutils
from ..utils import siteutils

class DiscoveringThread(I2PThread, object):

    def __init__(self, max_number_tries, max_time_trying):
        super(DiscoveringThread,self).__init__()
        self._max_number_tries = max_number_tries
        self._max_time_trying = max_time_trying

    def run(self):

        with db_session:
            # Doing until stop request
            while not self._stopped_event.isSet():

                status = siteutils.get_crawling_status()







        # To be overridden
        # response, start_time, end_time, elapsed_time = connection.connectThroughProxy(self._eepsite_url)
        response = request_conn.connectThroughProxy(self._eepsite_url)

        # Print CSV Line
        csv_line = ""

        # print(self._eepsite_url)
        csv_line += self._eepsite_url + "|" + str(response.status_code) + "|"
        csv_line += str(response.elapsed.total_seconds()) + "|" + str(self._rounds) + "|" + str(self._site_tries)
        print(csv_line)

    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        print("Stopping QoS for " + self._eepsite_url)

    def stop(self):
        self.on_stop()
        self._stopped_event.set()




