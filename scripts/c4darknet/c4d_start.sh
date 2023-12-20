#!/usr/bin/env bash

# This scripts is in charge of starting the manager and saving the PID for afterward stopping it
# Author: Emilio Figueras, 2020

root_path=/home/administrador/RMAGAN/projects/c4darknet/crawler

cd $root_path

source ~/anaconda3/etc/profile.d/conda.sh
conda activate py37
python manager.py &>/dev/null &
pid=$!

echo "[+] Launching manager with PID=$pid"
echo $pid > pid.txt 
