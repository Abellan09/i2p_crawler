#!/usr/bin/env bash

# Pulling code remotely for all instances
# Author: Roberto Magan, 2019

# list of VM instances
vm_list=`cat instances.txt`

# Remote scripts path
root_path=/home/administrador/RMAGAN/projects/I2P_Crawler

# Deployment
for vm in $vm_list;
do

	echo "[+] Pulling $vm from repository"
  	# Checking out previous versions
	ssh $vm "cd $root_path; git checkout crawler/settings.py crawler/database/dbsettings.py crawler/database/entities.py; git pull;"
	echo " "

done
