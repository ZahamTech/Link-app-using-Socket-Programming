import socket
import struct
import pickle
import threading
import pyaudio

# Server Configuration
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 1235))
server_socket.listen(4)

clients_connected = {}
clients_data = {}
count = 1

# Audio configurations
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def connection_requests():
    global count
    while True:
        print("Waiting for connection...")
        client_socket, address = server_socket.accept()

        print(f"Connection from {address} has been established")
        if len(clients_connected) == 4:
            client_socket.send('not_allowed'.encode())
            client_socket.close()
            continue
        else:
            client_socket.send('allowed'.encode())

        try:
            client_name = client_socket.recv(4096).decode('utf-8')
        except:
            print(f"{address} disconnected")
            client_socket.close()
            continue

        print(f"{address} identified itself as {client_name}")
        clients_connected[client_socket] = (client_name, count)

        # Image Receiving
        image_size_bytes = client_socket.recv(4096)
        image_size_int = struct.unpack('i', image_size_bytes)[0]

        client_socket.send('received'.encode())
        image_extension = client_socket.recv(1024).decode()

        b = b''
        while len(b) < image_size_int:
            image_bytes = client_socket.recv(1024)
            b += image_bytes

        clients_data[count] = (client_name, b, image_extension)

        clients_data_bytes = pickle.dumps(clients_data)
        clients_data_length = struct.pack('i', len(clients_data_bytes))

        client_socket.send(clients_data_length)
        client_socket.send(clients_data_bytes)

        if client_socket.recv(1024).decode() == 'image_received':
            client_socket.send(struct.pack('i', count))
            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())
                    data = pickle.dumps({'message': f"{client_name} joined the chat", 
                                         'extension': image_extension,
                                         'image_bytes': b, 'name': client_name, 
                                         'n_type': 'joined', 'id': count})
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)
                    client.send(data)

        count += 1
        t = threading.Thread(target=receive_data, args=(client_socket,))
        t.start()

def receive_data(client_socket):
    while True:
        try:
            data_bytes = client_socket.recv(4096)
            for client in clients_connected:
                if client != client_socket:
                    client.send('message'.encode())
                    client.send(data_bytes)

        except (ConnectionResetError, ConnectionAbortedError):
            handle_disconnect(client_socket)
            break

def handle_disconnect(client_socket):
    """Handle disconnection of a client."""
    print(f"{clients_connected[client_socket][0]} disconnected")
    for client in clients_connected:
        if client != client_socket:
            client.send('notification'.encode())
            data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
                                 'id': clients_connected[client_socket][1], 'n_type': 'left'})
            data_length_bytes = struct.pack('i', len(data))
            client.send(data_length_bytes)
            client.send(data)

    del clients_data[clients_connected[client_socket][1]]
    del clients_connected[client_socket]
    client_socket.close()


if __name__ == "__main__":
    connection_requests()
