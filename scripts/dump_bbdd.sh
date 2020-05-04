#!/usr/bin/env bash

# Dumping database
# Author: Roberto Magan, 2020

data_path=/home/administrador/datos

echo "--> Dumping I2P database"
mysqldump -u i2p -p4=XoG\!\*L i2p_database > $data_path/i2p/i2p_database.sql






