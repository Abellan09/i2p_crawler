#!/usr/bin/env bash

# Dumping database
# Author: Emilio Figueras, 2020

data_path=/home/administrador/datos
bbdd=$1

echo "--> Dumping database"
mysqldump -u $bbdd -p1Uchn53d $bbdd > $data_path/$bbdd.sql






