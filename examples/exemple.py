from jetracerpy.jetracer_client import JetRacerClient
import cv2



def handle_key_press(key, jetracer):
    """
    Handle key press events to control the JetRacer.
    :param key: Key code pressed.
    :param jetracer: JetRacerClient instance.
    """

    throttle_step = 0.15
    steering_step = 0.4

    if key == 27:  # ESC
        return False
    elif key == ord('z'):  # Increase throttle (move forward)
        current_throttle = min(1.0,  throttle_step)
        jetracer.send_rc_control(current_throttle, jetracer.current_steering)
    elif key == ord('s'):  # Decrease throttle (move backward)
        current_throttle = max(-1.0, -throttle_step-0.2)
        jetracer.send_rc_control(current_throttle, jetracer.current_steering)
    elif key == ord('q'):  # Turn left
        current_steering = max(-1.0, -steering_step)
        jetracer.send_rc_control(jetracer.current_throttle, current_steering)
    elif key == ord('d'):  # Turn right
        current_steering = min(1.0, steering_step)
        jetracer.send_rc_control(jetracer.current_throttle, current_steering)
    elif key == ord(' '):  # Stop
        jetracer.send_rc_control(0.0, 0.0)
    return True


if __name__ == "__main__":
    # Replace with your JetRacer's IP address
    #JETRACER_IP = "192.168.1.166"
    

    JETRACER_IP = "192.168.4.1"

    # Initialize the JetRacer client
    jetracer = JetRacerClient(jetracer_ip=JETRACER_IP)

    # Example usage of the SDK
    print("Starting JetRacer...")
    jetracer.start()

    jetracer.stream_on()

    # Get video capture object
    cap = cv2.VideoCapture(jetracer.rtsp_url)
    if not cap.isOpened():
        print("Failed to open video stream.")
        exit()

    print("Press 'ESC' to exit.")
    print("Use 'Z' (forward), 'S' (backward), 'Q' (left), 'D' (right), and 'Space' to stop.")

    # Initialize throttle and steering
    jetracer.current_throttle = 0.0
    jetracer.current_steering = 0.0
    jetracer.send_rc_control(jetracer.current_throttle, jetracer.current_steering)
    timex = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to receive frame from video stream.")
            break

        # Display the video stream
        cv2.imshow("JetRacer Stream", frame)
        
        # Read the electrical state already received in the background
        #state = jetracer.get_current_state()
        #print("Current JetRacer state:", state) 

        # Capture key press
        key = cv2.waitKey(1) & 0xFF
        # Handle key press for JetRacer control
        if not handle_key_press(key, jetracer):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    jetracer.stream_off()

    print("Stopping JetRacer...")
    jetracer.stop()
    jetracer.close()     # Ferme la socket et le thread

