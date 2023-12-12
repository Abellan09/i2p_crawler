#!/usr/bin/env bash

# Deleting files
# Author: Emilio Figueras, 2020

root_path=/home/administrador/RMAGAN/projects/c4darknetTOR/crawler

echo "[+] Creating folders..."
mkdir -p /home/administrador/datos/c4darknet/logs
mkdir -p /home/administrador/datos/c4darknet/spiders
mkdir -p /home/administrador/datos/c4darknet/spiders/ongoing
mkdir -p /home/administrador/datos/c4darknet/spiders/finished
echo " "

cd $root_path

echo "[+] Installing project dependencies ..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py37
pip install -r requirements.txt
echo " "

echo "[+] Deleting log and output files"
echo "--> Deleting log output"
find /home/administrador/datos/c4darknet/logs -type f -delete
echo "--> Deleting spiders output"
find /home/administrador/datos/c4darknet/spiders/ongoing -type f -delete
find /home/administrador/datos/c4darknet/spiders/finished -type f -delete
