#!/usr/bin/env bash

# Update code changes and reset the environment
# Author: Roberto Magan, 2019

root_path=$HOME/RMAGAN/projects/I2P_Crawler
i2p_data=$HOME/datos/i2p

echo "[+] Pulling from repository"
# Checking out previous versions
git checkout $root_path/crawler/manager.py
git checkout $root_path/crawler/database/dbsettings.py
git pull

echo "[+] Resetting the environment"
echo "--> Deleting spider output"
find $i2p_data/spiders -type f -delete
echo "--> Deleting log output"
rm $i2p_data/logs/*.log
echo "--> Deleting/creating database"
mysql -u i2p -p4=XoG\!\*L -e "drop database i2p_database; create database i2p_database"




