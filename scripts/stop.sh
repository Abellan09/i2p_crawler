#!/usr/bin/env bash

# Stops the crawling process gracefully
# Author: Roberto Magan, 2019

echo "Killing manager with PID=`cat pid.txt`"

# stopping the manager (hard stop)
kill -9 `cat pid.txt`

# stopping spiders (hard stop)
kill -9 `pgrep scrapy`