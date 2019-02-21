# -*- coding: utf-8 -*-

"""
    :mod:`i2pthread`
    ===========================================================================
    :synopsis: Parent methods to manage threads
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

import threading

class I2PThread(threading.Thread, object):
        
    def __init__(self):
        threading.Thread.__init__(self)        
        self._stopped_event = threading.Event()
        self._stopped_event.is_set = self._stopped_event.isSet
    
    def run(self):
        # To be overridden
        pass
    
    def on_stop(self):
        # Should be overridden to do some stuff on thread stop
        pass
    
    def stop(self):
        self.on_stop()
        self._stopped_event.set()