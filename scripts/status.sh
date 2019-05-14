#!/usr/bin/env bash

# Check the status of I2P routers and crawling processes on the involved VMs
# Author: Roberto Magan, 2019

# list of VM instances
vm_list=`cat instances.txt`

# Remote data folder
i2p_data=~/datos/i2p


# Deployment
for vm in $vm_list;
do
  echo "######### VM $vm ############"
  echo "[+] I2prouter status on $vm ..."
  ssh $vm "i2prouter status"

  echo "[+] Crawling process status on $vm ..."
  ssh $vm "ps -ef | grep manager"

  echo "[+] HD status $vm ..."
  ssh $vm "df -kh"

  echo "[+] MEM status $vm ..."
  ssh $vm "free -h"

  echo "######### VM $vm ############"

done
