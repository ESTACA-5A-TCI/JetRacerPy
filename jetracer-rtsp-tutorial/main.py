#!/usr/bin/env python3
"""
JetRacer RTSP and Control Script
Author: Your Name
Date: YYYY-MM-DD
Description: Control JetRacer via UDP and stream video with RTSP.
"""

import gi
# Initialize GStreamer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
import socket
import threading
import subprocess
from gi.repository import Gst, GstRtspServer, GObject
from jetracer.nvidia_racecar import NvidiaRacecar


Gst.init(None)
# Configurez l'adresse IP du client et le port pour le streaming
client_ip = "192.168.10.2"  # Remplacez par l'IP du client
video_port = 11111

# Fonction pour créer un point d'accès Wi-Fi
HOSTSPOT_SSID = "JetRacer_F2024"
PASSWORD = "JetRacer"

import subprocess
import sys

# Variables globales de configuration
WPA_SUPPLICANT_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"
HOSTAPD_CONF = "/etc/hostapd/hostapd.conf"
DNSMASQ_CONF = "/etc/dnsmasq.conf"
WIFI_INTERFACE = "wlan0"

def enable_station_mode(ssid, password):
    # Arrêter hostapd et dnsmasq si actifs
    subprocess.run(["sudo", "systemctl", "stop", "hostapd"], check=False)
    subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"], check=False)

    # Restaurer l'interface en mode normal (peut nécessiter de désactiver IP statique)
    subprocess.run(["sudo", "ifconfig", WIFI_INTERFACE, "down"], check=False)
    subprocess.run(["sudo", "ifconfig", WIFI_INTERFACE, "up"], check=False)

    # Mettre à jour wpa_supplicant.conf
    with open(WPA_SUPPLICANT_CONF, 'w') as f:
        f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
        f.write("update_config=1\n")
        f.write("country=FR\n\n")
        f.write("network={\n")
        f.write('    ssid="{}"\n'.format(ssid))
        f.write('    psk="{}"\n'.format(password))
        f.write("}\n")

    # Redémarrer le gestionnaire réseau (ex: NetworkManager)
    subprocess.run(["sudo", "systemctl", "restart", "network-manager"], check=True)
    print("Mode station activé. Tentative de connexion à {}".format(ssid))

def enable_hotspot_mode(ap_ssid, ap_password):
    # Arrêter NetworkManager si nécessaire
    subprocess.run(["sudo", "systemctl", "stop", "network-manager"], check=False)

    # Assigner une IP statique à l'interface
    subprocess.run(["sudo", "ifconfig", WIFI_INTERFACE, "192.168.4.1", "netmask", "255.255.255.0", "up"], check=True)

    # Créer/mettre à jour hostapd.conf
    with open(HOSTAPD_CONF, 'w') as f:
        f.write("interface={}\n".format(WIFI_INTERFACE))
        f.write("driver=nl80211\n")
        f.write("ssid={}\n".format(ap_ssid))
        f.write("hw_mode=g\n")
        f.write("channel=6\n")
        f.write("auth_algs=1\n")
        f.write("wmm_enabled=1\n")
        f.write("wpa=2\n")
        f.write("wpa_passphrase={}\n".format(ap_password))
        f.write("wpa_key_mgmt=WPA-PSK\n")
        f.write("rsn_pairwise=CCMP\n")

    # Créer/mettre à jour dnsmasq.conf
    with open(DNSMASQ_CONF, 'w') as f:
        f.write("interface={}\n".format(WIFI_INTERFACE))
        f.write("dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\n")
        f.write("dhcp-option=3,192.168.4.1\n")
        f.write("dhcp-option=6,192.168.4.1\n")

    # Démarrer hostapd et dnsmasq
    subprocess.run(["sudo", "systemctl", "start", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "start", "dnsmasq"], check=True)
    print("Point d'accès activé. SSID: {}, Mot de passe: {}".format(ap_ssid, ap_password))

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  {} station <ssid> <password>".format(sys.argv[0]))
        print("  {} ap <ap_ssid> <ap_password>".format(sys.argv[0]))
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "station":
        if len(sys.argv) != 4:
            print("Usage: {} station <ssid> <password>".format(sys.argv[0]))
            sys.exit(1)
        ssid = sys.argv[2]
        password = sys.argv[3]
        enable_station_mode(ssid, password)

    elif mode == "ap":
        if len(sys.argv) != 4:
            print("Usage: {} ap <ap_ssid> <ap_password>".format(sys.argv[0]))
            sys.exit(1)
        ap_ssid = sys.argv[2]
        ap_password = sys.argv[3]
        enable_hotspot_mode(ap_ssid, ap_password)

    else:
        print("Mode inconnu. Utilisez 'station' ou 'ap'.")




enable_hotspot_mode(HOSTSPOT_SSID , PASSWORD)
class RTSPServer:
    """RTSP Server to stream video from JetRacer's camera."""
    def __init__(self):
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()
        self.factory.set_launch((
            "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=120/1 "
            "! omxh264enc ! rtph264pay config-interval=1 name=pay0 pt=96"
        ))
        self.factory.set_shared(True)
        self.server.get_mount_points().add_factory("/test", self.factory)
        self.server.attach(None)
        self.streaming = False

    def start_streaming(self):
        """Start the RTSP video stream."""
        if not self.streaming:
            print("Starting video stream...")
            self.server.attach(None)
            self.streaming = True

    def stop_streaming(self):
        """Stop the RTSP video stream."""
        if self.streaming:
            print("Stopping video stream...")
            self.server.remove_mount_points()
            self.streaming = False

from jetcard.utils import power_mode #ip_address , power_usage, cpu_usage, gpu_usage, memory_usage, disk_usage
from jetcard import ina219
import os
class jetRacerStates:
    def __init__(self):
        adress_41 = os.popen("i2cdetect -y -r 1 0x41 0x41 | egrep '41' | '{print $2}'").read()
        adress_42 = os.popen("i2cdetect -y -r 1 0x42 0x42 | egrep '42' | '{print $2}'").read()
        if (adress_41 =='41\n'):
            self.ina = ina219.INA219(addr=0x41)
        elif (adress_42 == '42\n'):
            self.ina = ina219.INA219(addr=0x42)
        else:
            self.ina = None
    def get_jetracer_state(self):
        if self.ina is None:
            return "electric_state ?? ?? ?? ??"
        bus_voltage = self.ina.getBusVoltage_V()
        current     = self.ina.getgetCurrent_mA()/1000.0
        battery     = 100.0*(bus_voltage - 6.0)/2.4
        if (battery > 100): battery = 100
        elif (battery < 0): battery = 0
        return f"electric_state {power_mode()} {bus_voltage:.2f} {current:.2f} {battery:.2f}"
    

    
        
class JetRacerController:
    """Controller for handling JetRacer commands."""
    def __init__(self):
        self.car = NvidiaRacecar()
        self.car.throttle = 0
        self.car.steering = 0
        self.rtsp_server = RTSPServer()
        self.running = True

    def handle_command(self, command):
        """Process UDP commands and control the JetRacer."""
        command = command.strip().lower()
        if command == "start":
            print("Starting JetRacer...")
            self.car.throttle = 0
            self.car.steering = 0
        elif command == "stop":
            print("Stopping JetRacer...")
            self.car.throttle = 0
            self.car.steering = 0
        elif command.startswith("throttle"):
            try:
                value = float(command.split()[1])
                self.car.throttle = value
                print(f"Throttle set to: {value}")
            except Exception as e:
                print(f"Throttle command error: {e}")
        elif command.startswith("steering"):
            try:
                value = float(command.split()[1])
                self.car.steering = value
                print(f"Steering set to: {value}")
            except Exception as e:
                print(f"Steering command error: {e}")
        elif command.startswith("control"):
            try:
                parts = command.split()
                throttle_value = float(parts[1])
                steering_value = float(parts[2])
                self.car.throttle = throttle_value
                self.car.steering = steering_value
                print(f"Control command: Throttle={throttle_value}, Steering={steering_value}")
            except Exception as e:
                print(f"Control command error: {e}")
        elif command == "streamon":
            self.rtsp_server.start_streaming()
        elif command == "streamoff":
            self.rtsp_server.stop_streaming()
        elif command.startswith("connect_wifi"):
            _, ssid, password = command.split()
            enable_station_mode(ssid, password)
        elif command.startswith("create_hotspot"):
            #_, ssid, password = command.split()
            enable_hotspot_mode(HOSTSPOT_SSID , PASSWORD)
        #elif command == "disconnect_wifi":
        #    disconnect_wifi()
        else:
            print(f"Unknown command: {command}")

    def stop(self):
        """Stop the controller and cleanup."""
        self.running = False
        self.car.throttle = 0
        self.car.steering = 0
        self.rtsp_server.stop_streaming()


class UDPServer:
    """UDP Server to receive commands."""
    def __init__(self, host, port, controller):
        self.host = host
        self.port = port
        self.controller = controller

    def start(self):
        """Start the UDP server."""
        print(f"UDP server listening on {self.host}:{self.port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))

        while self.controller.running:
            try:
                data, addr = sock.recvfrom(1024)
                command = data.decode('utf-8')
                print(f"Received command: {command} from {addr}")
                self.controller.handle_command(command)
            except Exception as e:
                print(f"UDP server error: {e}")

        sock.close()


if __name__ == "__main__":
    controller = JetRacerController()
    udp_server = UDPServer("0.0.0.0", 8889, controller)

    # Start the UDP server in a separate thread
    udp_thread = threading.Thread(target=udp_server.start)
    udp_thread.start()

    try:
        # Main GObject loop for RTSP server
        loop = GObject.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        controller.stop()


