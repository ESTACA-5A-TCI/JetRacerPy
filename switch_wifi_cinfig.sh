#!/bin/bash
if [ "$1" == "ap" ]; then
	sudo systemctl stop wpa_supplicant
	sudo systemctl stop network-manager
	sudo ifconfig wlan0 192.168.4.1 netmask 255.255.255.0 up
	sudo systemctl start hostapd
	sudo systemctl start dnsmasq
elif [ "$1" == "client" ]; then
	sudo systemctl stop hostapd
	sudo systemctl stop dnsmasq
	sudo ifconfig wlan0 down
	sudo ifconfig wlan0 up
	sudo systemctl start wpa_supplicant
	sudo systemctl start network-manager
fi

