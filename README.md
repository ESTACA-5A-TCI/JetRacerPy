# JetRacer Configuration and Control Tutorial

## Introduction
This guide provides step-by-step instructions for setting up and controlling a JetRacer robot. It includes configuring Wi-Fi for access points or client mode, and using UDP commands to adjust throttle, steering, and video streaming with RTSP.

## Features
- Control throttle and steering individually or simultaneously.
- Start/stop video streaming via RTSP.
- Commands sent via UDP for minimal latency.
- Configure Wi-Fi as an access point or connect to an existing network.

## Requirements
- NVIDIA Jetson Nano (JetRacer configured).
- Python 3 installed on the Jetson Nano.
- Dependencies from `requirements.txt`.

---

## 1. Clone the Repository

1. Clone the repository in your `/home/[user name]/`:
   ```bash
   git clone -b python_server https://github.com/F-KHENFRI/JetRacerPy.git
   cd JetRacerPy
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Wi-Fi Setup

### Configuring a Wi-Fi Access Point
To set up a Wi-Fi access point on your Jetson Nano, run the following command:
```bash
python setup_wifi_access_point.py --ip-base 192.168.4.1 --ssid MyAccessPoint --password SecurePassword
```

### Configuring a Wi-Fi Client
To connect your Jetson Nano to an existing Wi-Fi network, use:
```bash
python setup_wifi_access_point.py --ssid MyWiFiNetwork --password WiFiPassword --configure-client
```

### Adding a Country Code for Client Configuration
If required, specify a country code during configuration:
```bash
python setup_wifi_access_point.py --ssid MyWiFiNetwork --password WiFiPassword --country US --configure-client
```

### Using the `switch_wifi_config.sh` Script
This script allows you to switch between Wi-Fi client and access point modes easily.

- To use the script, navigate to the script's directory and execute it with the desired mode:
  ```bash
  ./switch_wifi_config.sh <mode>
  ```
- Replace `<mode>` with one of the following options:
  - `client`: Switch to Wi-Fi client mode.
  - `ap`: Switch to Wi-Fi access point mode.

- Example usage:
  ```bash
  ./switch_wifi_config.sh client
  ./switch_wifi_config.sh ap
  ```

Ensure the script has executable permissions:
```bash
chmod +x switch_wifi_config.sh
```

---

## 3. Setup a Systemd Service

To automatically start the JetRacer RTSP server on boot:

1. Copy the service file to systemd:
   ```bash
   sudo cp jetracer_rtsp.service /etc/systemd/system/jetracer_rtsp.service
   ```

2. Reload systemd and enable the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable jetracer_rtsp.service
   ```

3. Start the service:
   ```bash
   sudo systemctl start jetracer_rtsp.service
   ```

4. Check the service status:
   ```bash
   sudo systemctl status jetracer_rtsp.service
   ```

---

## 4. Usage on Jetson

### Commands
- `start` - Start the JetRacer (sets throttle and steering to 0).
- `stop` - Stop the JetRacer.
- `throttle <value>` - Set throttle (-1.0 to 1.0).
- `steering <value>` - Set steering (-1.0 to 1.0).
- `control <throttle> <steering>` - Set throttle and steering simultaneously.
- `streamon` - Start video streaming.
- `streamoff` - Stop video streaming.
- `connect_wifi <SSID> <password>` - Connect to a Wi-Fi network.
- `connect_hotspot` - Configure as a Wi-Fi access point.

### Sending Commands
You can send commands via a UDP client, such as `netcat`:
```bash
echo "control 0.5 -0.3" | nc -u <ip_of_jetracer> 8889
echo "streamon" | nc -u <ip_of_jetracer> 8889
```

### Viewing the Video Stream
Use a video player like VLC to view the RTSP stream:
```
rtsp://<ip_of_jetracer>:8554/test
```

---


