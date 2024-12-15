#!/usr/bin/env python3
"""
Setup WIFI Access Point
Author: Fouad KHENFRI
Date: 15-12-2024
Description: Config Jetson to acceept create WIFI access point.
"""

import argparse

# Global configuration variables
WPA_SUPPLICANT_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"
HOSTAPD_CONF = "/etc/hostapd/hostapd.conf"
DNSMASQ_CONF = "/etc/dnsmasq.conf"
WIFI_INTERFACE = "wlan0"

def configure_dnsmasq(ip_base, wifi_interface, dnsmasq_conf_path):
    """
    Configure dnsmasq with a custom IP address and network interface.
    
    Arguments:
    - ip_base (str): Base IP address (e.g., '192.168.4.1').
    - wifi_interface (str): Name of the network interface (e.g., 'wlan0').
    - dnsmasq_conf_path (str): Path to the dnsmasq configuration file.
    """
    # Compute DHCP range based on the base IP
    dhcp_range_start = ip_base.rsplit('.', 1)[0] + '.2'  # e.g., 192.168.4.2
    dhcp_range_end = ip_base.rsplit('.', 1)[0] + '.20'   # e.g., 192.168.4.20
    
    # Write dnsmasq configuration
    with open(dnsmasq_conf_path, 'w') as f:
        f.write(f"interface={wifi_interface}\n")
        f.write(f"dhcp-range={dhcp_range_start},{dhcp_range_end},255.255.255.0,24h\n")
        f.write(f"dhcp-option=3,{ip_base}\n")  # Gateway address
        f.write(f"dhcp-option=6,{ip_base}\n")  # DNS server address

def configure_hostapd(ap_ssid, ap_password, wifi_interface, hostapd_conf_path):
    """
    Configure hostapd to set up a wireless access point with the given SSID and password.
    
    Arguments:
    - ap_ssid (str): SSID for the access point.
    - ap_password (str): Password for the access point.
    - wifi_interface (str): Name of the network interface (e.g., 'wlan0').
    - hostapd_conf_path (str): Path to the hostapd configuration file.
    """
    # Write hostapd configuration
    with open(hostapd_conf_path, 'w') as f:
        f.write(f"interface={wifi_interface}\n")
        f.write("driver=nl80211\n")
        f.write(f"ssid={ap_ssid}\n")
        f.write("hw_mode=g\n")
        f.write("channel=6\n")
        f.write("auth_algs=1\n")
        f.write("wmm_enabled=1\n")
        f.write("wpa=2\n")
        f.write(f"wpa_passphrase={ap_password}\n")
        f.write("wpa_key_mgmt=WPA-PSK\n")
        f.write("rsn_pairwise=CCMP\n")

def setup_wifi_access_point(ip_base, ap_ssid, ap_password):
    """
    Set up the Wi-Fi access point by configuring dnsmasq and hostapd.
    
    Arguments:
    - ip_base (str): Base IP address for the access point (e.g., '192.168.4.1').
    - ap_ssid (str): SSID for the access point.
    - ap_password (str): Password for the access point.
    """
    input("Create backup files for HOSTAPD_CONF and DNSMASQ_CONF, then press Enter to continue.")
    
    # Create/update the hostapd configuration
    configure_hostapd(ap_ssid, ap_password, WIFI_INTERFACE, HOSTAPD_CONF)
    
    # Create/update the dnsmasq configuration
    configure_dnsmasq(ip_base, WIFI_INTERFACE, DNSMASQ_CONF)

if __name__ == "__main__":
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="Set up a Wi-Fi access point using dnsmasq and hostapd.")
    parser.add_argument("--ip-base", required=True, help="Base IP address for the access point (e.g., '192.168.4.1').")
    parser.add_argument("--ssid", required=True, help="SSID for the Wi-Fi access point.")
    parser.add_argument("--password", required=True, help="Password for the Wi-Fi access point.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the setup function with parsed arguments
    setup_wifi_access_point(args.ip_base, args.ssid, args.password)
