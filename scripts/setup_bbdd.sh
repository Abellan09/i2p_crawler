#!/usr/bin/env bash

# Resetting database and schema
# Author: Roberto Magan, 2019

root_path=~/RMAGAN/projects/I2P_Crawler

echo "--> Deleting/creating database"
mysql -u i2p -p4=XoG\!\*L -e "drop database i2p_database; create database i2p_database"

echo "--> Populate database"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py27
python $root_path/crawler/database/populate.py
conda deactivate







