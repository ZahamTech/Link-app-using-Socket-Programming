import socket
import threading
import os

# Server Configuration
servr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servr_socket.bind(("127.0.0.1", 7000))  # Different port for file sharing
servr_socket.listen(4)

clients_connected5= {}

# Buffer size for file transfer
BUFFER_SIZE = 4096


SAVE_FOLDER = os.path.expanduser("C:/Users/PMLS/Desktop/Voice and File Sharing/server_downloads")
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def connection_requests():
    """Handles incoming client connection requests."""
    while True:
        print("Waiting for connection...")
        file_socket, address3 = servr_socket.accept()

        print(f"Connection from {address3} has been established")
        if len(clients_connected5) >= 4:
            file_socket.send('not_allowed'.encode())
            file_socket.close()
            continue
        else:
            file_socket.send('allowed'.encode())

        try:
            client_name5 = file_socket.recv(1024).decode('utf-8')
        except:
            print(f"{address3} disconnected during identification")
            file_socket.close()
            continue

        print(f"{address3} identified itself as {client_name5}")
        clients_connected5[file_socket] = client_name5

        threading.Thread(target=handle_file_transfer, args=(file_socket,)).start()


def broadcast_file(sender_socket, filename):
    """Broadcasts the received file to all connected clients except the sender."""
    file_path = os.path.join(SAVE_FOLDER, filename)

    with open(file_path, "rb") as f:
        file_data = f.read()

    for client_socket5 in clients_connected5:
        if client_socket5 != sender_socket:
            try:
                # Send file metadata
                metadata = f"{filename}|{len(file_data)}"
                client_socket5.send(metadata.encode('utf-8'))

                # Send file data
                client_socket5.sendall(file_data)
                print(f"File {filename} sent to {clients_connected5[client_socket5]}")
            except Exception as e:
                print(f"Error sending file to {clients_connected5[client_socket5]}: {e}")
                handle_disconnect5(client_socket5)


def handle_file_transfer(file_socket):
    """Handles file transfer from a client and broadcasts to others."""
    try:
        while True:
            # Receive file metadata
            metadata = file_socket.recv(BUFFER_SIZE).decode('utf-8')
            if not metadata:
                break

            filename, filesize = metadata.split('|')
            filesize = int(filesize)
            print(f"Receiving file: {filename} ({filesize} bytes) from {clients_connected5[file_socket]}")

            # Ensure the file is saved in the designated folder
            file_path = os.path.join(SAVE_FOLDER, filename)

            # Receive the file data
            with open(file_path, "wb") as f:
                bytes_received = 0
                while bytes_received < filesize:
                    data = file_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)

            print(f"File {filename} saved to {file_path}")

            # Broadcast the file to other clients
            broadcast_file(file_socket, filename)

    except Exception as e:
        print(f"Error receiving file from {clients_connected5[file_socket]}: {e}")
    finally:
        handle_disconnect5(file_socket)


def handle_disconnect5(file_socket):
    """Handle disconnection of a client."""
    if file_socket in clients_connected5:
        print(f"{clients_connected5[file_socket]} disconnected")
        del clients_connected5[file_socket]
        file_socket.close()


if __name__ == "__main__":
    connection_requests()
