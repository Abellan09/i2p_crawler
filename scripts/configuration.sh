#!/usr/bin/env bash

# Setting up crawling process config files
# Author: Roberto Magan, 2019

# root path
root_path=~/RMAGAN/projects/I2P_Crawler/

echo "[+] Setting up configuration files"
cp $root_path/scripts/dbsettings.py $root_path/crawler/database/
cp $root_path/scripts/settings.py $root_path/crawler/