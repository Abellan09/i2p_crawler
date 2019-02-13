'''
Created on 9 sept. 2016

@author: roberto
'''
import threading

from qos import request_conn

# import time
# import numpy as np


class I2PThread(threading.Thread, object):
        
    def __init__(self,eepsite_url,rounds,site_tries):
        threading.Thread.__init__(self)        
        self._stopped_event = threading.Event()
        self._stopped_event.is_set = self._stopped_event.isSet
        self._eepsite_url = eepsite_url
        self._rounds = rounds
        self._site_tries = site_tries
    
    def run(self):
        # To be overridden
        #response, start_time, end_time, elapsed_time = connection.connectThroughProxy(self._eepsite_url)
        response = request_conn.connectThroughProxy(self._eepsite_url)



        # Print CSV Line
        csv_line = ""

        #print(self._eepsite_url)
        csv_line+= self._eepsite_url + "|" + str(response.status_code) + "|"
        csv_line+= str(response.elapsed.total_seconds()) + "|" + str(self._rounds) + "|" + str(self._site_tries)
        print(csv_line)

    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        print("Stopping QoS for " + self._eepsite_url)
    
    def stop(self):
        self.on_stop()
        self._stopped_event.set()



        
        