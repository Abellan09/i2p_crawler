#!/usr/bin/env bash

# Stopping all the related processes on all the involved VMs
# Author: Roberto Magan, 2019

# list of VM instances
vm_list=`cat instances.txt`

# Remote scripts path
script_path=/home/administrador/RMAGAN/projects/I2P_Crawler/scripts

stop() {
  # $1 name of the remote VM
  vm=$1

  echo "######### VM $vm ############"
  
  # No processes in BBDD VM
  if [ $vm != 'i2pProjectBBDD' ]
  then
  	echo "[+] Stopping processes on $vm ..."
  	ssh $vm "cd $script_path; bash stop.sh"
  	echo " "
  fi
 
  echo "---- VM $vm -----"
  echo " "

}

if [ "$#" -gt 0 ]; then
	vm=$1
	stop $vm
else

	# list of all VM instances
	vm_list=`cat instances.txt`

	# Deployment
	for vm in $vm_list;
	do
	  stop $vm
	done

fi

