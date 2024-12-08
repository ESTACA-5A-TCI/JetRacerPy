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
        self.jetracer_ip = jetracer_ip
        self.udp_port = udp_port
        self.rtsp_url = f"rtsp://{jetracer_ip}:{rtsp_port}/test"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
        self.send_command(f"throttle {value}")

    def set_steering(self, value):
        """
        Set steering value.
        
        :param value: Steering value (-1.0 to 1.0)
        """
        self.send_command(f"steering {value}")

    def control(self, throttle, steering):
        """
        Control both throttle and steering.
        
        :param throttle: Throttle value (-1.0 to 1.0)
        :param steering: Steering value (-1.0 to 1.0)
        """
        self.send_command(f"control {throttle} {steering}")

    def stream_on(self):
        """Start the video stream."""
        self.send_command("streamon")

    def stream_off(self):
        """Stop the video stream."""
        self.send_command("streamoff")

    def view_stream(self):
        """
        View the RTSP video stream using OpenCV.
        """
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            print("Failed to open video stream.")
            return

        print("Press 'q' to exit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to receive frame from video stream.")
                break
            cv2.imshow("JetRacer Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
