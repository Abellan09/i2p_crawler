#!/usr/bin/env bash

# Deleting files
# Author: Emilio Figueras, 2020

root_path=~/RMAGAN/projects/I2P_Crawler

cd $root_path

echo "[+] Deleting log and output files"
echo "--> Deleting log output"
find logs -type f -delete
echo "--> Deleting spiders output"
find crawler/i2p/spiders/ongoing -type f -delete
find crawler/i2p/spiders/finished -type f -delete