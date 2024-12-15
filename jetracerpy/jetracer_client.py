import socket
import cv2


class JetRacerClient:
    """
    SDK Client for controlling the JetRacer via UDP and accessing its video stream.
    """
    def __init__(self, jetracer_ip, udp_port=8889, rtsp_port=8554):
        """
        Initialize the JetRacerClient.
        
        :param jetracer_ip: IP address of the JetRacer
        :param udp_port: UDP port for sending commands
        :param rtsp_port: RTSP port for video streaming
        """
        self.jetracer_ip_rtsp = "192.168.10.2"
        self.jetracer_ip = jetracer_ip
        self.udp_port = udp_port
        self.rtsp_url = f"rtsp://{self.jetracer_ip}:{rtsp_port}/test"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.current_throttle = 0.0
        self.current_steering = 0.0

    def send_command(self, command):
        """
        Send a command to the JetRacer.
        
        :param command: Command string to send
        """
        try:
            self.socket.sendto(command.encode('utf-8'), (self.jetracer_ip, self.udp_port))
            print(f"Command sent: {command}")
        except Exception as e:
            print(f"Failed to send command: {e}")

    def start(self):
        """Start the JetRacer."""
        self.send_command("start")

    def stop(self):
        """Stop the JetRacer."""
        self.send_command("stop")

    def set_throttle(self, value):
        """
        Set throttle value.
        
        :param value: Throttle value (-1.0 to 1.0)
        """
        self.current_throttle = value
        self.send_command(f"throttle {value}")

    def set_steering(self, value):
        """
        Set steering value.
        
        :param value: Steering value (-1.0 to 1.0)
        """
        self.current_steering = value
        self.send_command(f"steering {value}")

    def control(self, throttle, steering):
        """
        Control both throttle and steering.
        
        :param throttle: Throttle value (-1.0 to 1.0)
        :param steering: Steering value (-1.0 to 1.0)
        """
        self.current_throttle = throttle
        self.current_steering = steering
        self.send_command(f"control {throttle} {steering}")

    def stream_on(self):
        """Start the video stream."""
        self.send_command("streamon")

    def stream_off(self):
        """Stop the video stream."""
        self.send_command("streamoff")

    def set_throttle_gain(self, value):
        """ set throtle gain """
        self.send_command("throttle_gain {value}")
    
    def set_steering_gain(self, value):
        """ set throtle gain """
        self.send_command("steering_gain {value}")
    
    def set_steering_offset(self, value):
        """ set throtle gain """
        self.send_command("steering_offset {value}")
    
    
    def get_video_capture(self):
        """
        Return the RTSP video stream using OpenCV.
        """
        return cv2.VideoCapture(self.rtsp_url)
    
    

