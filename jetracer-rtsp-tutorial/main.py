#!/usr/bin/env python3
"""
JetRacer RTSP and Control Script
Author: Your Name
Date: YYYY-MM-DD
Description: Control JetRacer via UDP and stream video with RTSP.
"""

import gi
import socket
import threading
from gi.repository import Gst, GstRtspServer, GObject
from jetracer.nvidia_racecar import NvidiaRacecar

# Initialize GStreamer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
Gst.init(None)
# Configurez l'adresse IP du client et le port pour le streaming
client_ip = "192.168.10.2"  # Remplacez par l'IP du client
video_port = 11111

class RTSPServer:
    """RTSP Server to stream video from JetRacer's camera."""
    def __init__(self):
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()
        self.factory.set_launch((
            "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 "
            "! nvv4l2h264enc iframeinterval=15 control-rate=1 bitrate=4000000 preset=low-latency-hp "
            f"! h264parse ! rtph264pay config-interval=1 name=pay0 pt=96 ! udpsink host={client_ip} port={video_port}"
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


class JetRacerController:
    """Controller for handling JetRacer commands."""
    def __init__(self):
        self.car = NvidiaRacecar()
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