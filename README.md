# JetRacer Python Client SDK

This SDK allows you to control a JetRacer robot and view its video stream using Python.

## Features
- Control throttle and steering individually or together.
- Start and stop the robot.
- Start and stop the video stream.
- View the video stream in real-time using OpenCV.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jetracer-client.git
   cd jetracer-client
   ```

2. Install dependencies:
   ```bash 
   pip install opencv-python
   ```

## Usage

1. Import the `JetRacerClient` class.
2. Instantiate the client with the IP address of your JetRacer.
3. Use the provided methods to control the JetRacer and view the video stream.

### Example
```python
from jetracer_client import JetRacerClient

client = JetRacerClient("192.168.10.1")
client.start()
client.control(0.0, -0.3)
client.stream_on()
cap = client.get_video_capture()
_, frame = cap.read()
cv2.imshow("JetRacer Stream", frame)
client.stream_off()
client.stop()
```

## Commands

- `start()` - Start the JetRacer.
- `stop()` - Stop the JetRacer.
- `set_throttle(value)` - Set throttle (-1.0 to 1.0).
- `set_steering(value)` - Set steering (-1.0 to 1.0).
- `control(throttle, steering)` - Set throttle and steering simultaneously.
- `stream_on()` - Start the video stream.
- `stream_off()` - Stop the video stream.
- `get_video_capture()` - Get the video stream with cv2 capture object.

## Dependencies
- Python 3.x
- OpenCV (`opencv-python`)


---

### **How to Use**

1. Install Python dependencies:
   ```bash
   pip install opencv-python
   ```

2. Run the example script:
   ```bash
   python example.py
   ```

