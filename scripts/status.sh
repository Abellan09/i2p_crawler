#!/usr/bin/env bash

# Check the status of I2P routers and crawling processes on the involved VMs
# Author: Roberto Magan, 2019

# Remote scripts path
i2p_data=/home/administrador/datos

get_status() {
  # $1 name of the remote VM
  vm=$1

  echo "######### VM $vm ############"
  echo "[+] I2prouter status on $vm ..."
  ssh $vm "systemctl status i2p | grep -e \"Active\""
  echo " "

  echo "[+] Crawling process status on $vm ..."
  ssh $vm "ps -ef | grep manager.py"
  echo " "

  echo "[+] Floodfill status"
  ssh $vm "tail -n 6 $i2p_data/seeds/log_script.log"
  echo " "

  echo "[+] HD status $vm ..."
  ssh $vm "df -kh | grep -e \"sd\""
  echo " "

  echo "[+] MEM status $vm ..."
  ssh $vm "free -h"
  echo " "

  echo "---- VM $vm -----"
  echo " "

}

if [ "$#" -gt 0 ]; then
  vm=$1
  get_status $vm
else

# list of all VM instances
vm_list=`cat instances.txt`

# Deployment
for vm in $vm_list;
do
  get_status $vm
done

fi







