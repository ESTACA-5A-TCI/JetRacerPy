# JetRacer RTSP Control Tutorial
This tutorial demonstrates how to control a JetRacer robot via Wi-Fi, using UDP commands to adjust throttle, steering, and streaming video with RTSP.

## Features
- Control throttle and steering individually or together.
- Start/stop video streaming via RTSP.
- Commands sent via UDP for minimal latency.

## Requirements
- NVIDIA Jetson Nano (JetRacer configured).
- Python 3 installed on the Jetson Nano.
- Dependencies from `requirements.txt`.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jetracer-rtsp-tutorial.git
   cd jetracer-rtsp-tutorial
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python main.py
   ```

## Usage

### Commands
- `start` - Start the JetRacer (sets throttle and steering to 0).
- `stop` - Stop the JetRacer.
- `throttle <value>` - Set throttle (-1.0 to 1.0).
- `steering <value>` - Set steering (-1.0 to 1.0).
- `control <throttle> <steering>` - Set throttle and steering simultaneously.
- `streamon` - Start video streaming.
- `streamoff` - Stop video streaming.

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







