#!/usr/bin/env bash

# This scripts is in charge of starting the manager and saving the PID for afterward stopping it
# Author: Roberto Magan, 2019

root_path=~/RMAGAN/projects/I2P_Crawler
i2p_data=~/datos/i2p

cd $root_path/crawler

source ~/anaconda3/etc/profile.d/conda.sh
conda activate py27
python manager.py &>/dev/null &
pid=$!

echo "[+] Launching manager with PID=$pid"
echo $pid > pid.txt 




