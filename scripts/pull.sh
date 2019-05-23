#!/usr/bin/env bash

# Pulling code remotely for all instances
# Author: Roberto Magan, 2019

# Remote scripts path
root_path=/home/administrador/RMAGAN/projects/I2P_Crawler

pull() {
  # $1 name of the remote VM
  vm=$1

  echo "[+] Pulling $vm from repository"
  # Checking out previous versions
  ssh $vm "cd $root_path; git checkout crawler/settings.py crawler/database/dbsettings.py crawler/database/entities.py; git pull;"
  echo " "

}

if [ "$#" -gt 0 ]; then
	vm=$1
	pull $vm
else

	# list of all VM instances
	vm_list=`cat instances.txt`

	# Deployment
	for vm in $vm_list;
	do
	  pull $vm
	done

fi
