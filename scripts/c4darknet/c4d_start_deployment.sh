#!/usr/bin/env bash

# Setup, configure and run all the crawling processes on all the involved VMs
# Author: Emilio Figueras, 2020

if [ "$#" -lt 1 ]; then
  echo " "
  echo "Use: ./start_deployment.sh <instances> <darknet> <vm>"
  echo " "
  exit 1
fi


# list of VM instances
vm_list=`cat $1`

# Target darknet
darknet=$2

# Remote scripts path
script_path=/home/administrador/RMAGAN/projects/c4darknet/scripts/c4darknet/

deploy() {
  # $1 name of the remote VM
  vm=$1
  echo "######### VM $vm ############"

  bash c4d_pull.sh fake.txt $vm
  echo " "

  echo "[+] Configuring crawling process on $vm ..."
  ssh $vm "cd $script_path; bash c4d_configuration.sh $darknet"
  echo " "

  # Reseting BBDD and schema
  if [ $vm == 'c4darknet10' ]
  then
  	echo "[+] Setting up the file environment $vm ..."
  	ssh $vm "cd $script_path; bash c4d_setup_bbdd.sh $darknet"
  	echo " "
  else
    echo "[+] Setting up the file environment $vm ..."
  	ssh $vm "cd $script_path; bash c4d_setup.sh"
  	echo " "

    # Starting crawling process for VMs different from the VMs
    echo "[+] Starting the crawling process on $vm ..."
  	ssh $vm "cd $script_path; bash c4d_start.sh $vm"
  	echo " "
  fi
 
  echo "---- VM $vm -----"
  echo " "

}

if [ "$#" -eq 3 ]; then
	vm=$3
	deploy $vm
else

	# Deployment
	for vm in $vm_list;
	do
	  deploy $vm
	  echo "[+] Waiting 1 mins ..."
	  sleep 1m
	done

fi

