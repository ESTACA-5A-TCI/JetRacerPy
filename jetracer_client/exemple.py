from jetracer_client import JetRacerClient

if __name__ == "__main__":
    # Replace with your JetRacer's IP address
    JETRACER_IP = "192.168.10.1"
    
    client = JetRacerClient(jetracer_ip=JETRACER_IP)

    # Example usage of the SDK
    print("Starting JetRacer...")
    client.start()

    print("Setting throttle to 0.5 and steering to -0.3...")
    client.control(0.5, -0.3)

    input("Press Enter to start video streaming...")
    client.stream_on()
    client.view_stream()

    print("Stopping JetRacer...")
    client.stop()
