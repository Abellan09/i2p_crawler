#!/usr/bin/env bash

# Resetting database and schema
# Author: Roberto Magan, 2019

root_path=~/RMAGAN/projects/I2P_Crawler

echo "--> Dumping I2P database"
mysqldump -u i2p -p4=XoG\!\*L i2p_database > $root_path/i2p_database.sql






