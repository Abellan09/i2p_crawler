#!/usr/bin/env bash

# Deleting files
# Author: Roberto Magan, 2019

root_path=~/RMAGAN/projects/I2P_Crawler
i2p_data=~/datos/i2p

cd $root_path

echo "[+] Installing project dependencies in $vm ..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py27
pip install -r requirements.txt
echo " "

echo "[+] Deleting log and output files"
echo "--> Deleting spider output"
find $i2p_data/spiders -type f -delete
echo "--> Deleting log output"
rm $i2p_data/logs/*





