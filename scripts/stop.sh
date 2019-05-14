#!/usr/bin/env bash

# Stops the crawling process gracefully
# Author: Roberto Magan, 2019

echo "[+] Stopping crawling proces with UUID=`cat uuid.txt`"
echo "--> Killing manager with PID=`cat pid.txt`"
# stopping the manager (hard stop)`cat pid.txt`
kill -9 `cat pid.txt`
echo "--> Killing spiders ..."
# stopping spiders (hard stop)
kill -9 `pgrep scrapy`