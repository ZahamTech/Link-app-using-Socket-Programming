import socket
import threading
import pyaudio

# servera Configuration
servera_ip = "127.0.0.1"
servera_port = 9000

# Create and bind the servera socket
servera_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servera_socket.bind((servera_ip, servera_port))

# Connected clients dictionary
clients_connected1 = {}

# Audio configurations for low-latency
CHUNK = 512  # Smaller chunk for lower delay
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono for reduced data size
RATE = 22050  # Lower rate for reduced data size

def connection1_requests():
    threading.Thread(target=handle_client_data1).start()

def handle_client_data1():
    """Continuously listen for audio data and broadcast it to clients."""
    while True:
        try:
            data1, address1 = servera_socket.recvfrom(CHUNK * 2)  # Receive data
            if address1 not in clients_connected1:
                # Add client if not already connected
                if len(clients_connected1) < 4:
                    clients_connected1[address1] = True
                    print(f"New client connected: {address1}")
                    servera_socket.sendto(b'allowed', address1)
                else:
                    servera_socket.sendto(b'not_allowed', address1)
                    continue
            else:
                # Broadcast to all other clients
                broadcast_audio(address1, data1)
        except Exception as e:
            print(f"Error handling client data: {e}")

def broadcast_audio(sender_address1, data_bytes):
    """Broadcast audio data from one client to all others."""
    for client_address1 in list(clients_connected1.keys()):
        if client_address1 != sender_address1:
            try:
                servera_socket.sendto(data_bytes, client_address1)
            except Exception as e:
                print(f"Error sending audio to {client_address1}: {e}")
                handle_disconnect1(client_address1)

def handle_disconnect1(client_address1):
    """Handle disconnection of a client."""
    if client_address1 in clients_connected1:
        print(f"Client {client_address1} disconnected")
        del clients_connected1[client_address1]

if __name__ == "__main__":
    connection1_requests()
