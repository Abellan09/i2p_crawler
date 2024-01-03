#!/usr/bin/env bash

# Restarting all the crawling processes on all the involved VMs.
# Author: Emilio Figueras, 2020

script_path=/home/administrador/RMAGAN/projects/c4darknet/scripts/c4darknet/
data_path=/home/administrador/datos

for bbdd in i2p tor freenet;
do

	echo "[+] Dumping database of $bbdd"
	ssh c4darknet10 "cd $script_path; bash c4d_dump_database.sh $bbdd"
	echo " "

	echo "[+] Download database $bbdd.sql"
	scp c4darknet10:$data_path/$bbdd.sql $bbdd.sql
	echo " "

	echo " "
done

