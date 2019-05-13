#!/usr/bin/env bash

# Stops the crawling process gracefully
# Author: Roberto Magan, 2019

echo "Killing manager with PID=`cat pid.txt`"

# stopping the manager
kill -n SIGINT `cat pid.txt`

