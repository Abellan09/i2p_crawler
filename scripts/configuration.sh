#!/usr/bin/env bash

# Setting up crawling process config files
# Author: Roberto Magan, 2019

root_path=$HOME/RMAGAN/projects/I2P_Crawler

# ssh name, previous configured in .ssh/config
host=$1

echo "[+] Setting up configuration files on $host"
scp dbsettings.py $host:$root_path/crawler/database/
scp settings.py $host:$root_path/crawler/