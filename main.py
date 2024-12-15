#!/usr/bin/env python3
"""
JetRacer RTSP and Control Script
Author: Fouad KHENFRI
Date: 12-12-2024
Description: Control JetRacer via UDP and stream video with RTSP.
"""

import gi
# Initialize GStreamer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
import socket
import threading
import subprocess
import time
import os

from gi.repository import Gst, GstRtspServer, GObject
from jetracer.nvidia_racecar import NvidiaRacecar
from jetcard.utils import power_mode #ip_address , power_usage, cpu_usage, gpu_usage, memory_usage, disk_usage
from jetcard import ina219



Gst.init(None)

class WifiConfig:
    # Variables globales de configuration
    WPA_SUPPLICANT_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"
    HOSTAPD_CONF = "/etc/hostapd/hostapd.conf"
    DNSMASQ_CONF = "/etc/dnsmasq.conf"
    WIFI_INTERFACE = "wlan0"
    AP_IP = "192.168.4.1" 
    

    @classmethod
    def enable_station_mode(cls, ssid, password):
        # Arrêter hostapd et dnsmasq si actifs
        subprocess.run(["systemctl", "stop", "hostapd"], check=False)
        subprocess.run(["systemctl", "stop", "dnsmasq"], check=False)

        # Restaurer l'interface en mode normal (peut nécessiter de désactiver IP statique)
        subprocess.run(["ifconfig", cls.WIFI_INTERFACE, "down"], check=False)
        subprocess.run(["ifconfig", cls.WIFI_INTERFACE, "up"], check=False)

        # Mettre à jour wpa_supplicant.conf
        subprocess.run(["nmcli", "device", "wifi", "connect", ssid,  "password", password], check=False)

        # Redémarrer le gestionnaire réseau (ex: NetworkManager)
        subprocess.run(["systemctl", "start", "wpa_supplicant"], check=True)
        subprocess.run(["systemctl", "start", "network-manager"], check=True)
        print("Mode station activé. Tentative de connexion à {}".format(ssid))

    @classmethod
    def enable_hotspot_mode(cls):
        # Arrêter NetworkManager si nécessaire
        subprocess.run(["systemctl", "stop", "wpa_supplicant"], check=False)
        subprocess.run(["systemctl", "stop", "network-manager"], check=False)

        # Assigner une IP statique à l'interface
        subprocess.run(["ifconfig", cls.WIFI_INTERFACE, cls.AP_IP, "netmask", "255.255.255.0", "up"], check=True)

        # Démarrer hostapd et dnsmasq
        subprocess.run(["systemctl", "start", "hostapd"], check=True)
        subprocess.run(["systemctl", "start", "dnsmasq"], check=True)
        


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
        self.mounts  = self.server.get_mount_points()
        self.mounts.add_factory("/test", self.factory)
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
            self.mounts.remove_factory("/test")
            self.streaming = False


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
    def __init__(self, ap_ip):
        self.car = NvidiaRacecar()
        self.car.throttle = 0
        self.car.steering = 0
        self.rtsp_server = RTSPServer()
        self.wifi_config = WifiConfig()
        self.jetracer_states = jetRacerStates()
        self.wifi_config.AP_IP = ap_ip
        self.running = True
        self.can_receive_command = False

    def handle_command(self, command):
        """Process UDP commands and control the JetRacer."""
        command = command.strip().lower()
        response = None
        if command == "start":
            print("Starting JetRacer...")
            self.car.throttle = 0
            self.car.steering = 0
            self.can_receive_command = True
            response = "ok"
        
        elif command == "stop":
            print("Stopping JetRacer...")
            self.car.throttle = 0
            self.car.steering = 0
            self.can_receive_command = False
            response = "ok"
        
        elif command.startswith("throttle") and self.can_receive_command:
            try:
                value = float(command.split()[1])
                self.car.throttle = value
                print(f"Throttle set to: {value}")
            except Exception as e:
                print(f"Throttle command error: {e}")
        
        elif command.startswith("steering") and self.can_receive_command:
            try:
                value = float(command.split()[1])
                self.car.steering = value
                print(f"Steering set to: {value}")
            except Exception as e:
                print(f"Steering command error: {e}")
        
        elif command.startswith("control") and self.can_receive_command:
            try:
                parts = command.split()
                throttle_value = float(parts[1])
                steering_value = float(parts[2])
                self.car.throttle = throttle_value
                self.car.steering = steering_value
                print(f"Control command: Throttle={throttle_value}, Steering={steering_value}")
            except Exception as e:
                print(f"Control command error: {e}")
        
        elif command == "streamon" and self.can_receive_command:
            self.rtsp_server.start_streaming()
            response = "streaming on"
        
        elif command == "streamoff" and self.can_receive_command:
            self.rtsp_server.stop_streaming()
            response = "streaming off"

        elif command.startswith("connect_wifi") and self.can_receive_command:
            _, ssid, password = command.split()
            self.wifi_config.enable_station_mode(ssid, password)
            response = "wifi setup"
        
        elif command.startswith("connect_hotspot") and self.can_receive_command:
            #_, ssid, password = command.split()
            self.wifi_config.enable_hotspot_mode()
            response = "hostspot setup"

        elif command.startswith("set_throttle_gain") and self.can_receive_command:
            # Usage : "set_throttle_gain 1.2"
            try:
                value = float(command.split()[1])
                self.car.throttle_gain = value
                response = f"throttle_gain {value}"
            except Exception as e:
                print(f"Error setting throttle_gain: {e}")

        elif command.startswith("set_steering_gain") and self.can_receive_command:
            # Usage : "set_steering_gain 1.1"
            try:
                value = float(command.split()[1])
                self.car.steering_gain = value
                response = f"steering_gain {value}"
            except Exception as e:
                print(f"Error setting steering_gain: {e}")

        elif command.startswith("set_steering_offset") and self.can_receive_command:
            # Usage : "set_steering_offset 0.05"
            try:
                value = float(command.split()[1])
                self.car.steering_offset = value
                response = f"steering_offset {value}"
            except Exception as e:
                print(f"Error setting steering_offset: {e}")
        
        elif command.startswith("get_throttle_gain") and self.can_receive_command:
            value = self.car.throttle_gain
            response = f"throttle_gain {value}"

        elif command.startswith("get_steering_gain") and self.can_receive_command:
            value = self.car.steering_gain
            response = f"steering_gain {value}"

        elif command.startswith("get_steering_offset") and self.can_receive_command:
            value = self.car.steering_offset 
            response = f"steering_offset {value}"

        else:
            if self.can_receive_command:
                response = f"Unknown command: {command}"
            else:
                response = "Send 'start' command"
        
        return response

    def stop(self):
        """Stop the controller and cleanup."""
        self.running = False
        self.car.throttle = 0
        self.car.steering = 0
        self.rtsp_server.stop_streaming()

# -------------------------------------------
#  Classe UDPServer
# -------------------------------------------
class UDPServer:
    """UDP Server to receive commands et envoyer l'état périodiquement."""
    def __init__(self, host, port, controller, send_interval=1.0):
        """
        :param host: IP d'écoute (ex: "0.0.0.0")
        :param port: Port d'écoute UDP
        :param controller: Instance de JetRacerController
        :param send_interval: Intervalle en secondes pour envoyer l'état
        """
        self.host = host
        self.port = port
        self.controller = controller
        self.send_interval = send_interval

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        self.last_addr = None  # On mémorise la dernière adresse qui nous a envoyé une commande

    def start(self):
        """Démarre le serveur UDP et un thread pour envoi périodique des states."""
        print(f"UDP server listening on {self.host}:{self.port}")

        # Thread pour la réception de commandes
        recv_thread = threading.Thread(target=self.recv_commands)
        recv_thread.daemon = True
        recv_thread.start()

        # Thread pour l'envoi périodique du state
        send_thread = threading.Thread(target=self.send_state_periodically)
        send_thread.daemon = True
        send_thread.start()

        # Boucle principale : on attend que le controller s'arrête (Ctrl+C ou autre)
        while self.controller.running:
            time.sleep(0.5)

        self.sock.close()

    def recv_commands(self):
        """Boucle de réception des commandes UDP."""
        while self.controller.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                command = data.decode('utf-8')
                print(f"Received command: {command} from {addr}")

                # Mémorise l'adresse pour pouvoir lui renvoyer des infos
                self.last_addr = addr

                # On demande au controller de traiter la commande
                response = self.controller.handle_command(command)
                
                # S'il y a une réponse, on la renvoie au client
                if response is not None:
                    self.sock.sendto(response.encode('utf-8'), addr)

            except Exception as e:
                print(f"UDP server error: {e}")
                break

    def send_state_periodically(self):
        """Envoi périodique de l'état électrique de la JetRacer."""
        while self.controller.running:
            time.sleep(self.send_interval)
            if self.last_addr is not None:
                # Récupère l'état actuel
                state_str = self.controller.jetracer_states.get_jetracer_state()
                # Envoie à la dernière adresse connue
                self.sock.sendto(state_str.encode('utf-8'), self.last_addr)

# -------------------------------------------
#  Programme principal
# -------------------------------------------
if __name__ == "__main__":
    controller = JetRacerController()
    controller.wifi_config.enable_hotspot_mode()
    udp_server = UDPServer("0.0.0.0", 8889, controller, send_interval=2.0)

    # Démarre tout dans le thread principal
    server_thread = threading.Thread(target=udp_server.start)
    server_thread.start()

    try:
        # Main GObject loop for RTSP server
        loop = GObject.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        controller.stop()
        server_thread.join()