import socket
import cv2
import threading
import time

class JetRacerClient:
    """
    SDK Client for controlling the JetRacer via UDP and accessing its video stream.
    Inspired by the Tello drone code structure for asynchronous reception.
    """

    DEFAULT_UDP_PORT = 8889   # UDP port for sending commands
    DEFAULT_RTSP_PORT = 8554  # Default RTSP port
    DEFAULT_TIMEOUT = 2.0     # Timeout in seconds for receiving the server's response
    
    def __init__(self, jetracer_ip, 
                 udp_port=DEFAULT_UDP_PORT, 
                 rtsp_port=DEFAULT_RTSP_PORT, 
                 rtsp_ip=None, 
                 timeout=DEFAULT_TIMEOUT,
                 listen_state=True):
        """
        Initialize the JetRacerClient.
        
        :param jetracer_ip: IP address of the JetRacer (for UDP commands)
        :param udp_port:    UDP port for sending commands
        :param rtsp_port:   RTSP port for video streaming
        :param rtsp_ip:     (optionnel) IP for RTSP streaming if different from jetracer_ip
        :param timeout:     Timeout in seconds for receiving responses
        :param listen_state:If True, launch a background thread to receive states
        """
        self.jetracer_ip = jetracer_ip
        self.udp_port = udp_port
        self.timeout = timeout
        
        if rtsp_ip is None:
            rtsp_ip = jetracer_ip
        self.rtsp_url = f"rtsp://{rtsp_ip}:{rtsp_port}/test"
        
        # UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        
        # Thread de réception : on peut stocker réponses et state
        self.running = False
        self.response_thread = None
        
        # État électrique (pour stocker le dernier state reçu)
        self.power_mode = None
        self.voltage = None
        self.current = None
        self.battery = None
        self.state_lock = threading.Lock()
        
        # Variables courantes
        self.current_throttle = 0.0
        self.current_steering = 0.0
        
        # Si l’utilisateur veut écouter l’état en asynchrone
        if listen_state:
            self.start_listener()

    # ----------------------------------------------------------------
    #  Thread de réception pour toutes les réponses & états électriques
    # ----------------------------------------------------------------
    def start_listener(self):
        """Lance un thread qui écoute en permanence les messages UDP arrivant du JetRacer."""
        self.running = True
        self.response_thread = threading.Thread(target=self._udp_receiver, daemon=True)
        self.response_thread.start()
    
    def _udp_receiver(self):
        """Boucle de réception UDP en arrière-plan. Parse les réponses et l'état électrique."""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = data.decode('utf-8').strip()
                # On peut décider si c'est un state (ex : "electric_state ...") ou une réponse
                if message.startswith("electric_state"):
                    self._parse_electric_state(message)
                else:
                    print(f"[UDP Listener] From {addr}: {message}")
            except socket.timeout:
                # Pas de data, on loop
                continue
            except Exception as e:
                print(f"[UDP Listener] Error: {e}")
                break

    def _parse_electric_state(self, message):
        """
        Parse un message de type : 
        "electric_state <power_mode> <voltage> <current> <battery>"
        Exemple: "electric_state Normal 7.20 1.50 45.00"
        """
        parts = message.split()
        # [0] = electric_state
        # [1] = power_mode
        # [2] = voltage
        # [3] = current
        # [4] = battery
        if len(parts) == 5:
            with self.state_lock:
                self.power_mode = parts[1]
                self.voltage = float(parts[2])
                self.current = float(parts[3])
                self.battery = float(parts[4])
                print(f"[STATE] mode={self.power_mode} volt={self.voltage} current={self.current} batt={self.battery}")

    def stop_listener(self):
        """Stoppe le thread de réception des états."""
        self.running = False
        if self.response_thread:
            self.response_thread.join()
            self.response_thread = None

    # ----------------------------------------------------------------
    #  Fonctions d'envoi de commandes (avec ou sans retour direct)
    # ----------------------------------------------------------------
    def send_command(self, command):
        """
        Envoie une commande au JetRacer sans forcément attendre de réponse.
        
        :param command: Command string to send
        """
        try:
            self.socket.sendto(command.encode('utf-8'), (self.jetracer_ip, self.udp_port))
            print(f"[send_command] Command sent: {command}")
        except Exception as e:
            print(f"[send_command] Failed to send command: {e}")

    def send_command_return_response(self, command):
        """
        Envoie une commande UDP et attend (bloquant) UNE réponse.
        Utile si vous voulez un retour direct (ex: 'ok' / 'error').
        
        :param command: Command string
        :return: réponse du serveur ou None si timeout
        """
        try:
            self.socket.sendto(command.encode('utf-8'), (self.jetracer_ip, self.udp_port))
            print(f"[send_command_return_response] Command sent: {command}")
            
            response, addr = self.socket.recvfrom(1024)
            response_str = response.decode('utf-8').strip()
            print(f"[send_command_return_response] Received response from {addr}: {response_str}")
            return response_str

        except socket.timeout:
            print("[send_command_return_response] No response from server (timeout).")
            return None
        except Exception as e:
            print(f"[send_command_return_response] Error: {e}")
            return None

    # ----------------------------------------------------------------
    #  Méthodes de contrôle
    # ----------------------------------------------------------------
    def start(self):
        """Start (enable) the JetRacer controls."""
        response = self.send_command_return_response("start")
        if "ok" == response:
            self.can_send_commands = True
        return response

    def stop(self):
        """Stop (disable) the JetRacer controls."""
        response = self.send_command_return_response("stop")
        if "ok" == response:
            self.can_send_commands = False
        return response

    def send_rc_control(self, throttle, steering):
        """
        Envoi une commande combinée (throttle & steering).
        :param throttle: [-1.0, 1.0]
        :param steering: [-1.0, 1.0]
        """
        self.current_throttle = throttle
        self.current_steering = steering
        self.send_command(f"control {throttle} {steering}")

    def stream_on(self):
        """Start the JetRacer's RTSP video stream."""
        return self.send_command_return_response("streamon")

    def stream_off(self):
        """Stop the JetRacer's RTSP video stream."""
        return self.send_command_return_response("streamoff")

    def set_throttle_gain(self, value):
        """Set the throttle gain factor."""
        return self.send_command_return_response(f"set_throttle_gain {value}")

    def set_steering_gain(self, value):
        """Set the steering gain factor."""
        return self.send_command_return_response(f"set_steering_gain {value}")

    def set_steering_offset(self, value):
        """Set the steering offset."""
        return self.send_command_return_response(f"set_steering_offset {value}")

    def get_throttle_gain(self):
        """Request the current throttle_gain from the JetRacer."""
        return self.send_command_return_response("get_throttle_gain")

    def get_steering_gain(self):
        """Request the current steering_gain from the JetRacer."""
        return self.send_command_return_response("get_steering_gain")

    def get_steering_offset(self):
        """Request the current steering_offset from the JetRacer."""
        return self.send_command_return_response("get_steering_offset")

    def connect_wifi(self, ssid, password):
        """Tell the JetRacer to switch to Wi-Fi station mode."""
        return self.send_command_return_response(f"connect_wifi {ssid} {password}")

    def connect_hotspot(self):
        """Tell the JetRacer to switch to hotspot mode."""
        return self.send_command_return_response("connect_hotspot")

    # ----------------------------------------------------------------
    #  Gestion du flux vidéo
    # ----------------------------------------------------------------
    def get_video_capture(self):
        """
        Get the RTSP video stream using OpenCV.
        
        :return: cv2.VideoCapture object
        """
        return cv2.VideoCapture(self.rtsp_url)

    # ----------------------------------------------------------------
    #  Récupération de l'état actuel
    # ----------------------------------------------------------------
    def get_current_state(self):
        """
        Renvoie un dict avec l'état électrique stocké.
        Permet de lire power_mode, voltage, current, battery, etc.
        """
        with self.state_lock:
            return {
                "power_mode": self.power_mode,
                "voltage": self.voltage,
                "current": self.current,
                "battery": self.battery
            }

    # ----------------------------------------------------------------
    #  Nettoyage
    # ----------------------------------------------------------------
    def close(self):
        """
        Stop the listener thread and close the UDP socket.
        """
        self.stop_listener()
        self.socket.close()
        print("[JetRacerClient] Closed socket and stopped listener.")
