'''
Created on 9 sept. 2016

@author: roberto
'''
import threading
from qos import connection
# import time
# import numpy as np

class I2PThread(threading.Thread, object):
        
    def __init__(self,eepsite_url,rounds):
        threading.Thread.__init__(self)        
        self._stopped_event = threading.Event()
        self._stopped_event.is_set = self._stopped_event.isSet
        self._eepsite_url = eepsite_url
        self._rounds = rounds
    
    def run(self):
        # To be overridden
        response, start_time, end_time, elapsed_time = connection.connectThroughProxy(self._eepsite_url)
        response = response.split('\r\n')
        print(response)
        protocol = response[0].split(' ')[0]
        responseCode = response[0].split(' ')[1]

        # Print CSV Line
        csv_line = ""
        if response:
            #print(self._eepsite_url)
            csv_line+= self._eepsite_url + "|" + protocol + "|" + responseCode + "|"
            csv_line+= str(start_time) + "|" + str(end_time) + "|" + str(elapsed_time) + "|" + str(self._rounds)
            print(csv_line)

    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        print("Stopping QoS for " + self._eepsite_url)
    
    def stop(self):
        self.on_stop()
        self._stopped_event.set()



        
        