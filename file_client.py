import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Client Configuration
SEVER_IP = "127.0.0.1"
SEVER_PORT = 7000
BUFFER_SIZE = 4096

# Connect to server
file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_socket.connect((SEVER_IP, SEVER_PORT))

# Identify client
client_name3 = "Client1"  # Change this for each client
file_socket.send(client_name3.encode('utf-8'))

# Downloads folder
DOWNLOADS_DIR = os.path.expanduser("receive_file")
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)
# Downloads folder
Discarded_DIR = os.path.expanduser("Discarded_Files")
if not os.path.exists(Discarded_DIR):
    os.makedirs(Discarded_DIR)

# Global variable to hold file details
pending_file = None
pending_filesize = 0
pending_filename = ""

def handle_file_metadata():
    """Listen for incoming file metadata and prompt the user for action."""
    global pending_file, pending_filesize, pending_filename

    try:
        while True:
            # Receive file metadata
            metadata = file_socket.recv(BUFFER_SIZE).decode('utf-8')
            if not metadata:
                continue  # Skip if no data received

            # Debug print for received metadata
            print(f"Received metadata: {metadata}")

            # Validate metadata format
            if '|' not in metadata:
                print("Invalid metadata format")
                continue

            pending_filename, pending_filesize = metadata.split('|', 1)
            if not pending_filename or not pending_filesize.isdigit():
                print("Invalid metadata content")
                continue

            pending_filesize = int(pending_filesize)

            # Notify user about incoming file
            prompt_label.config(
                text=f"Incoming file: {pending_filename} ({pending_filesize} bytes)."
            )
            receive_button.config(state=tk.NORMAL)
            discard_button.config(state=tk.NORMAL)

            # Pause to wait for user action
            action_event.wait()
            action_event.clear()
    except Exception as e:
        print(f"Error receiving file metadata: {e}")

def receive_file():
    """Receive the pending file and save it."""
    global pending_file, pending_filesize, pending_filename

    if not pending_filename:
        return

    try:
        filepath = os.path.join(DOWNLOADS_DIR, pending_filename)
        with open(filepath, "wb") as f:
            bytes_received = 0
            while bytes_received < pending_filesize:
                chunk = file_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)

        # Notify the user and reset the state
        messagebox.showinfo(
            "File Received", f"File '{pending_filename}' saved to Received Files."
        )
    except Exception as e:
        messagebox.showerror("Error", f"Error receiving file: {e}")
    finally:
        reset_state()

def discard_file():
    """Discard the pending file."""
    global pending_filename
    if not pending_filename:
        return

    try:
        filepath = os.path.join(Discarded_DIR, pending_filename)
        with open(filepath, "wb") as f:
            bytes_received = 0
            while bytes_received < pending_filesize:
                chunk = file_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)

        # Notify the user and reset the state
        messagebox.showinfo("File Discarded", f"File '{pending_filename}' discarded.")
    except Exception as e:
        messagebox.showerror("Error", f"Error receiving file: {e}")
    finally:
        reset_state()

    try:
        filepath = os.path.join(Discarded_DIR, pending_filename)
        with open(filepath, "wb") as f:
            bytes_received = 0
            while bytes_received < pending_filesize:
                chunk = file_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)

        # Notify the user and reset the state
        messagebox.showinfo("File Discarded", f"File 'File '{pending_filename}' discarded.")
    except Exception as e:
        messagebox.showerror("Error", f"Error receiving file: {e}")
    finally:
        reset_state()

def reset_state():
    """Reset the global state and disable buttons."""
    global pending_file, pending_filesize, pending_filename

    pending_file = None
    pending_filesize = 0
    pending_filename = ""

    prompt_label.config(text="No incoming files.")
    receive_button.config(state=tk.DISABLED)
    discard_button.config(state=tk.DISABLED)

    # Notify the metadata thread to resume listening
    action_event.set()

def send_file():
    """Handles file selection and sending."""
    filepath = filedialog.askopenfilename()
    if not filepath:
        return

    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        metadata = f"{filename}|{filesize}"

        # Send metadata
        file_socket.send(metadata.encode('utf-8'))

        # Send file data
        with open(filepath, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                file_socket.sendall(chunk)

        messagebox.showinfo("File Sent", f"File '{filename}' sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send file: {e}")

def on_close():
    """Handle closing the application."""
    file_socket.close()
    root.destroy()

def create_gui():
    """Setup and launch the GUI."""
    global root, prompt_label, receive_button, discard_button, action_event

    # GUI Setup
    root = tk.Tk()
    root.title("File Sharing Client")
    root.geometry("400x200")

    # Common button style
    button_style = {
        "font": ("Arial", 12),
        "bg": "lightgray",
        "fg": "black",
        "activebackground": "darkgray",
        "activeforeground": "white",
        "relief": "raised",
    }

    # Notification area
    prompt_label = tk.Label(
        root, text="No incoming files.", font=("Arial", 12, "bold"), bg="white",
        fg="black", wraplength=580, relief="solid", bd=2
    )
    prompt_label.place(x=40, y=20, width=420, height=35)

    # Receive button
    receive_button = tk.Button(
        root, text="Receive File", command=receive_file, state=tk.DISABLED, **button_style
    )
    receive_button.place(x=40, y=100, width=100, height=30)

    # Discard button
    discard_button = tk.Button(
        root, text="Discard File", command=discard_file, state=tk.DISABLED, **button_style
    )
    discard_button.place(x=40, y=130, width=100, height=30)

    # Send button
    send_button = tk.Button(
        root, text="Send File", command=send_file, **button_style
    )
    send_button.place(x=40, y=70, width=100, height=30)

    # Event to coordinate file reception
    action_event = threading.Event()

    # Start metadata handling thread
    threading.Thread(target=handle_file_metadata, daemon=True).start()

    # Set close event
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()