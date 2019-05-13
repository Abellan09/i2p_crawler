#!/usr/bin/env bash

# Setting up crawling process config files
# Author: Roberto Magan, 2019

root_path=../crawler

echo "[+] Setting up configuration files"
cp dbsettings.py $root_path/database/
cp settings.py $root_path