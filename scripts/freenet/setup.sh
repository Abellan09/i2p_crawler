#!/usr/bin/env bash

# Deleting files
# Author: Emilio Figueras, 2020

root_path=~/RMAGAN/projects/I2P_Crawler
cd $root_path

echo "[+] Creating folders..."
mkdir -p logs
mkdir -p crawler/i2p/spiders/ongoing
mkdir -p crawler/i2p/spiders/finished
echo " "

cd $root_path/crawler

echo "[+] Installing project dependencies ..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py37
pip install -r requirements.txt
echo " "

echo "[+] Deleting log and output files"
echo "--> Deleting log output"
find logs -type f -delete
echo "--> Deleting spiders output"
find crawler/i2p/spiders/ongoing -type f -delete
find crawler/i2p/spiders/finished -type f -delete