# -*- coding: utf-8 -*-

from i2pthread import thread
import threading
import time
import pandas as pd
from utils import siteutils

list_seeds = siteutils.get_initial_seeds('../../data/extracted_eepsites.txt')

# Test 400 error
# columns = ['url','protocol','code','start','end','duration','runid']
# df_qos = pd.read_csv('qos_analysis.csv',names=columns,delimiter="|")
# list_seeds = df_qos[(df_qos['code'] == 400)]['url'].tolist()
# print(list_seeds)

#list_seeds = ["rmagan.i2p"]

# Setting up experiment test
max_rounds = 10
rounds = 0
site_tries = 5
while rounds < max_rounds:
    for seed in list_seeds:

        seed = "http://" + seed
        #print(seed)
        #print(seed)
        for i in range(site_tries):
	    time.sleep(0.15)
            i2pt = thread.I2PThread(seed,rounds,i)
            i2pt.start()

        time.sleep(0.3)
        #print("Starting " + i2pt.name)

    # We should wait until all current round thread finish
    # for i in threading.enumerate():
    #      if i is not threading.currentThread():
    #          print("Waiting for " + i.name)
    #          i.join()

    #print("Round " + str(rounds))

    rounds += 1
