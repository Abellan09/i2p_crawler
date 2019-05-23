#!/usr/bin/env bash

# Setup, configure and run all the crawling processes on all the involved VMs
# Author: Roberto Magan, 2019

# list of VM instances
vm_list=`cat instances.txt`

# Remote scripts path
script_path=/home/administrador/RMAGAN/projects/I2P_Crawler/scripts

# Deployment
for vm in $vm_list;
do

  echo "######### VM $vm ############"
  echo "[+] Setting up process on $vm ..."
  ssh $vm "cd $script_path; bash setup.sh"
  echo " "

  echo "[+] Configuring crawling process on $vm ..."
  ssh $vm "cd $script_path; bash configuration.sh"
  echo " "

  # Starting crawling process for VMs different from the VMs
  if [ $vm != 'i2pProjectBBDD' ]
  then
  	echo "[+] Starting the crawling process on $vm ..."
  	ssh $vm "cd $script_path; bash start.sh $vm"
  	echo " "
  fi
  echo "---- VM $vm -----"

done
