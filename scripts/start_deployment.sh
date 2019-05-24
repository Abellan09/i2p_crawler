#!/usr/bin/env bash

# Setup, configure and run all the crawling processes on all the involved VMs
# Author: Roberto Magan, 2019

# list of VM instances
vm_list=`cat instances.txt`

# Remote scripts path
script_path=/home/administrador/RMAGAN/projects/I2P_Crawler/scripts

deploy() {
  # $1 name of the remote VM
  vm=$1

  echo "######### VM $vm ############"

  bash pull.sh $vm
  echo " "

  echo "[+] Configuring crawling process on $vm ..."
  ssh $vm "cd $script_path; bash configuration.sh"
  echo " "

  # Reseting BBDD and schema
  if [ $vm == 'i2pProjectBBDD' ]
  then
  	echo "[+] Setting up the file environment $vm ..."
  	ssh $vm "cd $script_path; bash setup_bbdd.sh"
  	echo " "
  else
        echo "[+] Setting up the file environment $vm ..."
  	ssh $vm "cd $script_path; bash setup.sh"
  	echo " "

        # Starting crawling process for VMs different from the VMs
        echo "[+] Starting the crawling process on $vm ..."
  	ssh $vm "cd $script_path; bash start.sh $vm"
  	echo " "
  fi
 
  echo "---- VM $vm -----"
  echo " "

}

if [ "$#" -gt 0 ]; then
	vm=$1
	deploy $vm
else

	# list of all VM instances
	vm_list=`cat instances.txt`

	# Deployment
	for vm in $vm_list;
	do
	  deploy $vm
	done

fi

