import subprocess
import os

'''
cmd = "scrapy crawl i2p -a url=http://anoncoin.i2p -o i2p/spiders/finished/anoncoin.i2p.json"
os.system(cmd)
'''

next_site = "anoncoin.i2p"
next_site2 = "i2pdarknetmap.i2p"
param1 = "url=http://" + next_site
param2 = "i2p/spiders/ongoing/" + next_site + ".json"
param3 = "url=http://" + next_site2
param4 = "i2p/spiders/ongoing/" + next_site2 + ".json"
subprocess.Popen(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2], shell=False)
subprocess.Popen(["scrapy", "crawl", "i2p", "-a", param3, "-o", param4], shell=False)
