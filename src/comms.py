import socket

# konfigurisati firewall kod pi ako se paket ne recievuje

def send_udp_data():
    PICO_IP_ADDRESS = "192.168.1.174"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0) # da ne freezuje script

    print("Type 'LED_ON' or 'LED_OFF' to control the Pico 2 W. Type 'exit' to quit.")

    while True:
        message = input("Enter command to send: ")
        if message.lower() == 'exit':
            break

        try:
            sock.sendto(message.encode('utf-8'), (PICO_IP_ADDRESS, UDP_PORT))

            data, server = sock.recvfrom(1024)
            print(f"Response from Pico: {data.decode('utf-8')}")

        except TimeoutError:
            print("No packet received within 2 seconds.")

        except Exception as e:
            print(f"An error occurred: {type(e).__name__} - {e}")


    sock.close()
