#!/usr/bin/env bash

# Check the status of I2P routers and crawling processes on the involved VMs
# Author: Roberto Magan, 2019

if [ "$#" -lt 1 ]; then
  echo " "
  echo "Use: ./status.sh <instances> <vm>"
  echo " "
  exit 1
fi

# list of all VM instances
vm_list=`cat $1`

# Remote scripts path
i2p_data=/home/administrador/datos

get_status() {
  # $1 name of the remote VM
  vm=$1

  echo "######### VM $vm ############"
  echo "[+] I2prouter status on $vm ..."
  ssh $vm "systemctl status i2p | grep -e \"Active\""
  echo " "

  echo "[+] I2prouter proxy on $vm ..."
  ssh $vm "netstat -utl | grep 4444"
  echo " "

  echo "[+] Crawling process status on $vm ..."
  ssh $vm "ps -ef | grep manager.py"
  echo " "

  echo "[+] Ongoing spiders $vm ..."
  ssh $vm "pgrep scrapy | wc -l"
  echo " "

  echo "[+] Floodfill status"
  ssh $vm "tail -n 6 $i2p_data/seeds/log_script.log"
  echo " "

# Reseting BBDD and schema
#  if [ $vm == 'i2pProjectBBDD' ]
#  then
  	echo "[+] HD status $vm ..."
        ssh $vm "df -kh | grep -e \"sd\""
        echo " "

        echo "[+] MEM status $vm ..."
        ssh $vm "free -h"
        echo " "
#  fi

  echo "---- VM $vm -----"
  echo " "
  echo " "

}

if [ "$#" -eq 2 ]; then
	vm=$2
	get_status $vm
else

	# Deployment
	for vm in $vm_list;
	do
	  get_status $vm
	done

fi







