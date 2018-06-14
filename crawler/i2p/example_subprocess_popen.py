import subprocess

next_site = "anoncoin.i2p"
param1 = "url=http://" + next_site
param2 = "i2p/spiders/ongoing/" + next_site + ".json"
subprocess.Popen(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2], shell=False)
