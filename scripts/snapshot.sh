#!/usr/bin/env bash

# Experiment snapsho
# Author: Roberto Magan, 2019

if [ "$#" -lt 1 ]; then
  echo " "
  echo "Use: ./snapshot.sh <instances> <vm>"
  echo " "
  exit 1
fi


# list of VM instances
vm_list=`cat $1`

# local snapshot folder
lfolder=$3

# Remote scripts path
root_path=/home/administrador/RMAGAN/projects/I2P_Crawler
script_path=$root_path/scripts

# ts of snapshop
ts=`date +"%d%m%y%H%M%S"`

snapshot() {
  # $1 name of the remote VM
  vm=$1
  echo "######### VM $vm ############"

  mkdir -p $ts/$vm-backup

  # Dumping BBDD
  if [ $vm == 'i2pProjectBBDD' ]
  then
  	echo "[+] Dumping bbdd $vm ..."
  	ssh $vm "cd $script_path; bash dump_bbdd.sh"
	scp $vm:$root_path/i2p_database.sql $ts/$vm-backup
  	echo " "
  else
        echo "[+] Backing up $vm ..."
	rsync -av --exclude='*nltk*' $vm:/home/administrador/datos/ $ts/$vm-backup
  	echo " "
  fi
 
  echo "---- VM $vm -----"
  echo " "

}

if [ "$#" -eq 2 ]; then
	vm=$2
	snapshot $vm
else

	# Deployment
	for vm in $vm_list;
	do
	  snapshot $vm
	  echo "[+] Waiting 1 mins ..."
	  sleep 1m
	done

fi

