#!/usr/bin/env bash

# Setting up crawling process config files
# Author: Emilio Figueras, 2020

if [ $# -lt 1 ];
then
	echo "Please give me the name of the darknet to be crawled: i2p, freenet or tor"
	exit 1
fi

darknet=$1

# root path
root_path=/home/administrador/RMAGAN/projects/c4darknet

echo "[+] Setting up configuration files"
cp $root_path/scripts/c4darknet/$darknet/config/settings.py $root_path/crawler/
cp $root_path/scripts/c4darknet/$darknet/config/connection_settings.py $root_path/crawler/database/
cp $root_path/scripts/c4darknet/$darknet/config/darknetsettings.py $root_path/crawler/darknet/
