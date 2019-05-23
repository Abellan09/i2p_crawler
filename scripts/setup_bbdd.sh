#!/usr/bin/env bash

# Resetting database and schema
# Author: Roberto Magan, 2019

echo "--> Deleting/creating database"
mysql -u i2p -p4=XoG\!\*L -e "drop database i2p_database; create database i2p_database"

echo "--> Populate database"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py27
python crawler/database/populate.py
conda deactivate







