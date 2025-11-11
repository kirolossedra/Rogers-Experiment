#!/bin/bash
set -v
set -e

sudo rmmod qmi_wwan
sleep 2
sudo modprobe qmi_wwan_q
sleep 2
sudo rmmod qmi_wwan_q
sleep 2
sudo modprobe qmi_wwan_q
sleep 2
sudo $HOME/Research/Rogers/5G/qconnectmanager/quectel-CM -4 -6
