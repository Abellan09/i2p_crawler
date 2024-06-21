#!/usr/bin/env bash

# Deleting files
# Author: Emilio Figueras, 2020

root_path=/home/administrador/RMAGAN/projects/c4darknet/crawler
data_path=/home/administrador/datos/c4darknet/

mkdir -p $data_path

echo "[+] Deleting log and output files"
echo "--> Deleting log output"
find $data_path/logs -type f -delete
echo "--> Deleting spiders output"
find $data_path/spiders/ongoing -type f -delete
find $data_path/spiders/finished -type f -delete
echo "--> Deleting uuid.txt"
rm -f $root_path/uuid.txt
