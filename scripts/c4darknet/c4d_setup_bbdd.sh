#!/usr/bin/env bash

# Resetting database and schema
# Author: Emilio Figueras

root_path=/home/administrador/RMAGAN/projects/c4darknetTOR/crawler
cd $root_path

echo "--> Deleting/creating database"
mysql -u c4darknet -p1Uchn53d -e "drop database c4darknet; create database c4darknet"

echo "--> Populate database"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py37
python populate.py
conda deactivate


