#!/usr/bin/env bash

# Deleting files
# Author: Roberto Magan, 2019

i2p_data=~/datos/i2p

echo "[+] Deleting log and output files"
echo "--> Deleting spider output"
find $i2p_data/spiders -type f -delete
echo "--> Deleting log output"
rm $i2p_data/logs/*





