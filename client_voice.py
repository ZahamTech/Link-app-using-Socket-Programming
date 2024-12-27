import socket
import threading
import pyaudio
import tkinter as tk
from tkinter import messagebox

# Client Configuration
servera_ip = "127.0.0.1"
servera_port = 9000
client_name1 = "Client1"  # Change this for different clients

# Audio configurations for low-latency
CHUNK = 512  # Smaller chunk for reduced delay
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono for smaller data size
RATE = 22050  # Reduced rate for lower latency

# Global variables
audio_stream = None
audio_socket = None
is_call_active = False
playback_stream = None

def start_call():
    """Initiates the call by setting up audio streams and communication."""
    global audio_socket, audio_stream, is_call_active
    if is_call_active:
        messagebox.showinfo("Info", "Call is already active!")
        return

    try:
        # Create a UDP socket
        audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        audio_socket.sendto(client_name1.encode('utf-8'), (servera_ip, servera_port))

        # Start audio streaming
        pyaudio_instance = pyaudio.PyAudio()
        audio_stream = pyaudio_instance.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        global playback_stream
        playback_stream = pyaudio_instance.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True
        )

        is_call_active = True
        threading.Thread(target=send_audio).start()
        threading.Thread(target=receive_audio).start()

        messagebox.showinfo("Info", "Call started successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start call: {e}")

def send_audio():
    """Streams audio data from the microphone to the server."""
    global audio_socket, audio_stream, is_call_active
    try:
        while is_call_active:
            data1 = audio_stream.read(CHUNK, exception_on_overflow=False)
            audio_socket.sendto(data1, (servera_ip, servera_port))
    except Exception as e:
        print(f"Error in sending audio: {e}")

def receive_audio():
    """Receives audio data from the server and plays it."""
    global audio_socket, is_call_active, playback_stream

    try:
        while is_call_active:
            data1, _ = audio_socket.recvfrom(CHUNK * 2)  # Adjust buffer for incoming data
            if not data1:
                break
            playback_stream.write(data1)
    except Exception as e:
        print(f"Error in receiving audio: {e}")

def end_call():
    """Terminates the call by stopping streams and closing sockets."""
    global audio_socket, audio_stream, playback_stream, is_call_active

    if not is_call_active:
        messagebox.showinfo("Info", "No active call to end!")
        return

    try:
        is_call_active = False

        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()

        if playback_stream:
            playback_stream.stop_stream()
            playback_stream.close()

        if audio_socket:
            audio_socket.close()

        messagebox.showinfo("Info", "Call ended successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to end call: {e}")

# GUI Setup
def create_gui():
    """Creates the graphical user interface for the client."""
    window = tk.Tk()
    window.title("Voice Call Client")
    window.geometry("300x200")
    start_button = tk.Button(window, text="Start Call", command=start_call, width=15, height=2)
    start_button.pack(pady=20)
    end_button = tk.Button(window, text="End Call", command=end_call, width=15, height=2)
    end_button.pack(pady=20)
    window.mainloop()

if __name__ == "__main__":
    create_gui()
