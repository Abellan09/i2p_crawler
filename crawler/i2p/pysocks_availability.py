# -*- coding: utf-8 -*-

from i2pthread import thread
import threading
import time
import pandas as pd

with open('data/extracted_eepsites.txt') as seeds:
    list_seeds = seeds.readlines()

# Test 400 error
# columns = ['url','protocol','code','start','end','duration','runid']
# df_qos = pd.read_csv('qos_analysis.csv',names=columns,delimiter="|")
# list_seeds = df_qos[(df_qos['code'] == 400)]['url'].tolist()
# print(list_seeds)

#list_seeds = ["rmagan.i2p"]

# Setting up experiment test
max_rounds = 1
rounds = 0
while rounds < max_rounds:
    for seed in list_seeds[0:1]:
        #print(seed)
        #print(seed)
        seed = str.replace(seed,'\n','')
        seed = str.replace(seed,'\r','')
        #print(seed)
        seed = "http://" + seed
        #print(seed)
        #print(seed)
        for i in range(3):
            time.sleep(0.3)
            i2pt = thread.I2PThread(seed,rounds)
            i2pt.start()
        #print("Starting " + i2pt.name)

    # We should wait until all current round thread finish
    # for i in threading.enumerate():
    #      if i is not threading.currentThread():
    #          print("Waiting for " + i.name)
    #          i.join()

    #print("Round " + str(rounds))

    rounds += 1
