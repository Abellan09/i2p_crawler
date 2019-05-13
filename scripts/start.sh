#!/usr/bin/env bash

# This scripts is in charge of starting the manager and saving the PID for afterward stopping it
# Author: Roberto Magan, 2019

root_path=$HOME/RMAGAN/projects/I2P_Crawler

conda activate py27
python $root_path/crawler/manager.py &>/dev/null &
pid=$!

echo "[+] Launching manager with PID=$pid"
echo $pid > pid.txt 




