import pickle
import socket
import struct
import sys
import time
import tkinter as tk
import threading
import cv2
import pyaudio
from PIL import Image, ImageTk

root = tk.Tk()
mylabel = tk.Label(root)
row = 0
column = 1
mylabel.grid(row=row, column=0)
username = "ttt"

cap = cv2.VideoCapture(0)

vidintentionmsg = "vid"
audiointentionmsg = "audio"
leaveintentionmsg = "leave"

SERVER_MAINPORT = 1111 #vid port
SERVER_AUDIOPORT= 1112 #audio port
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
SERVER_IP = "192.168.1.174"
SERVER_ADDR = (SERVER_IP, SERVER_MAINPORT) #vid addr
SERVER_AUDIO_ADDR = (SERVER_IP, SERVER_AUDIOPORT) #audio addr

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect(SERVER_ADDR)

server_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_audio_socket.connect(SERVER_AUDIO_ADDR)

CHUNK = 1024  # Number of audio samples per frame
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate in Hz
AUDIOFORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()
stream = p.open(format=AUDIOFORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

output_stream = p.open(format=AUDIOFORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       output=True)



def sendtfunc():
    while True:

        ret, frame = cap.read()

        if ret:
            # Convert the frame from OpenCV's BGR format to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an image from the NumPy array
            img = Image.fromarray(rgb_frame)
            sendvid(img)
            photo = ImageTk.PhotoImage(img)

            # Set the image on the label
            mylabel.config(image=photo)
            mylabel.image = photo

            # Schedule the update_frame function to run again after 10 milliseconds
            time.sleep(1 / 30)

            # TODO make audio here
            send_audio()


def send_audio():
    data = stream.read(CHUNK)

    serialized_data = pickle.dumps(data)
    message_size = struct.pack("L", len(serialized_data))  # taking the data size "L" stands for long

    server_audio_socket.sendall(message_size)
    server_audio_socket.sendall(serialized_data)


def recvtfunc():
    column = 1
    labelsdict = {}
    while True:
        if handle_recv_vid(labelsdict,column) :
            column=column+1
        handle_recv_audio()


def handle_recv_vid(labelsdict, column):
    a = False
    message_size = serversocket.recv(struct.calcsize("L"))
    message_size = struct.unpack("L", message_size)[0]
    data = b""
    while len(data) < message_size:
        packet = serversocket.recv(message_size - len(data))
        if not packet:
            break
        data += packet
    frametuple = pickle.loads(data)
    lblid = frametuple[0]
    if lblid not in labelsdict:
        lbl = tk.Label(root)
        lbl.grid(row=row, column=column)
        labelsdict.update({lblid: lbl})
        a = True
    photo = ImageTk.PhotoImage(frametuple[-1])
    labelsdict.get(lblid).config(image=photo)
    labelsdict.get(lblid).image = photo
    return a


def handle_recv_audio():
    message_size = server_audio_socket.recv(struct.calcsize("L"))
    message_size = struct.unpack("L", message_size)[0]
    data = b""
    while len(data) < message_size:
        packet = server_audio_socket.recv(message_size - len(data))
        if not packet:
            break
        data += packet
    audiodata = pickle.loads(data)
    output_stream.write(audiodata)


def on_close():  # triggers when client closes the window , notifying the server to close the socket
    print("closing program , disconnecting you from the server ....")
    message = leaveintentionmsg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    serversocket.send(send_length)
    serversocket.send(message)
    root.destroy()  # close window
    time.sleep(0.5)
    sys.exit()  # TODO find exit program func


def sendvid(img):
    message = vidintentionmsg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    serversocket.send(send_length)
    serversocket.send(message)

    l = (username, img)
    serialized_data = pickle.dumps(l)

    message_size = struct.pack("L", len(serialized_data))  # taking the data size "L" stands for long

    serversocket.sendall(message_size)
    serversocket.sendall(serialized_data)





sendthread = threading.Thread(target=sendtfunc)
sendthread.start()
recvthread = threading.Thread(target=recvtfunc)
recvthread.start()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

