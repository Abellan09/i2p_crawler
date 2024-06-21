#!/usr/bin/env bash

# Resetting database and schema
# Author: Emilio Figueras

if [ $# -lt 1 ];
then
	echo "Please give me the name of the darknet to be crawled: i2p, freenet or tor"
	exit 1
fi

#database user
user=$1

root_path=/home/administrador/RMAGAN/projects/c4darknet/crawler
cd $root_path

echo "--> Deleting/creating database"
mysql -u $user -p1Uchn53d -e "drop database $user; create database $user"

echo "--> Populate database"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py37
python populate.py
conda deactivate


