import math
import pickle
import socket
import secrets
import struct
import threading
import time
import hashlib
from Crypto.Cipher import AES

from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256


from PIL import Image, ImageTk
import cv2
import tkinter as tk

G=2243 #two big primes
N=1399
secret_key=None

username="kkk"
vid_intention="vid"

dsa_key = DSA.generate(2048)
dsa_public_key=dsa_key.public_key().export_key()
signer = DSS.new(dsa_key, 'fips-186-3')
server_dsa_public_key=None
verifier=None



root = tk.Tk()
mylabel = tk.Label(root)
row=0
column=1
mylabel.grid(row=row, column=0)
labelsdict={}

SERVER_MAINPORT=1111
HEADER=64
FORMAT='utf-8'
SERVER_IP="192.168.1.174"
SERVER_ADDR=(SERVER_IP,SERVER_MAINPORT)

serversocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversocket.connect(SERVER_ADDR)

cap = cv2.VideoCapture(0)

def send_thread():
    while True:

        send_vid()



def recv_thread():
    print("FD")
    while True:
        intention=recv_msg_from_server()
        if intention==vid_intention:
            recv_vid_tuple_from_the_server()







def send_vid():
    ret, frame = cap.read()

    if ret:
        # Convert the frame from OpenCV's BGR format to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create an image from the NumPy array
        img = Image.fromarray(rgb_frame)
        send_img(img)
        photo = ImageTk.PhotoImage(img)

        # Set the image on the label
        mylabel.config(image=photo)
        mylabel.image = photo

        # Schedule the update_frame function to run again after 10 milliseconds
        time.sleep(1 / 30)

def recv_vid_tuple_from_the_server():
    message_size = serversocket.recv(struct.calcsize("L"))
    message_size = struct.unpack("L", message_size)[0]
    data = b""
    while len(data) < message_size:
        packet = serversocket.recv(message_size - len(data))
        if not packet:
            break
        data += packet
    tuple_package_to_dec = pickle.loads(data)
    try:
        hash_obj = SHA256.new(tuple_package_to_dec[0])
        verifier.verify(hash_obj, tuple_package_to_dec[3])

        cipher_dec = AES.new(secret_key, AES.MODE_EAX, tuple_package_to_dec[2])
        p_frametuple = cipher_dec.decrypt_and_verify(tuple_package_to_dec[0], tuple_package_to_dec[1])
        frametuple = pickle.loads(p_frametuple)
        usrname_lblid = frametuple[0]
        if usrname_lblid not in labelsdict:
            lbl = tk.Label(root)
            global column, row
            lbl.grid(row=row, column=column)
            column += 1
            labelsdict.update({usrname_lblid: lbl})
        photo = ImageTk.PhotoImage(frametuple[-1])
        labelsdict.get(usrname_lblid).config(image=photo)
        labelsdict.get(usrname_lblid).image = photo
        print("i recved an img!!!")
    except ValueError:
        print("msg not authentic ):")


def send_img(img):

    global secret_key
    t=(username,img)
    pt=pickle.dumps(t)
    cipher = AES.new(secret_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(pt)

    hash_obj = SHA256.new(ciphertext) #creating a signature
    signature =signer.sign(hash_obj)

    t2=(ciphertext,tag,cipher.nonce,signature)#ciphertxt is the usr+img tuple
    serialized_data = pickle.dumps(t2)
    message_size = struct.pack("L", len(serialized_data))  # taking the data size "L" stands for long

    send_message_to_server(vid_intention)
    serversocket.sendall(message_size)
    serversocket.sendall(serialized_data)#pickle( AES(pickle(usr,img)) ,tag ,nounce,signature)
    print("image sent from the client")



def diffie_key_exchange():
    private_x=secrets.randbits(16) #random 8 bits num
    print(f"private x ={private_x}")
    A=modular_exponentiation(G,private_x,N)
    print(f"A: {A}")
    send_message_to_server(A)
    b=recv_msg_from_server()
    b=int(b)
    print(f"got b from client {b}")
    secret_key=modular_exponentiation(b,private_x,N)


    # all of this is for converting the shared number from diffie to a 128bit key for the AES
    key_bytes = secret_key.to_bytes(3, byteorder='big', signed=False).rjust(16, b'\x00')  # converting to bytestring
    key_padded = key_bytes.rjust(16, b'\x00')
    salt = b'saltvalue'  # Random salt value (keep secret)
    iterations = 1000  # Number of PBKDF2 iterations (choose appropriate value)
    key_128bit = hashlib.pbkdf2_hmac('sha256', key_padded, salt, iterations, dklen=16)
    print(f"MYSECRETE KEY IS {key_128bit}")

    return key_128bit






def send_message_to_server(msg):
    message = str(msg).encode(FORMAT)  # exchange a,b
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    serversocket.send(send_length)
    serversocket.send(message)


def recv_msg_from_server():
    msg_length = serversocket.recv(HEADER).decode(FORMAT)  # waiting on this line till i get a msg from the client
    if msg_length:  # if msg not empty
        msg_length = int(msg_length)
        m = serversocket.recv(msg_length).decode(FORMAT)
        return m

def modular_exponentiation(a, b, c):#returns a^b mod c
    result = 1
    a = a % c
    while b > 0:
        if b % 2 == 1:
            result = (result * a) % c
        b = b // 2
        a = (a * a) % c
    return result

def dsa_public_key_exchange():
    serialized_data = pickle.dumps(dsa_public_key)
    message_size = struct.pack("L", len(serialized_data))  #sending my public dsa key to the server...
    serversocket.sendall(message_size)
    serversocket.sendall(serialized_data)
    print(f"client public dsa key : {dsa_public_key}")


    message_size2 = serversocket.recv(struct.calcsize("L")) #getting server's public dsa key
    message_size2 = struct.unpack("L", message_size2)[0]
    data = b""
    while len(data) < message_size2:
        packet = serversocket.recv(message_size2 - len(data))
        if not packet:
            break
        data += packet
    serverdsa_key = pickle.loads(data)
    print(f"server public dsa key : {serverdsa_key}")

    global server_dsa_public_key
    server_dsa_public_key=DSA.import_key(serverdsa_key)  #storing the server's key
    global verifier
    verifier = DSS.new(server_dsa_public_key, 'fips-186-3')


def init_conn():
    global secret_key
    secret_key=diffie_key_exchange()
    dsa_public_key_exchange()
    thread = threading.Thread(target=send_thread)
    thread.start()
    print("send thread started")
    thread2=threading.Thread(target=recv_thread)
    thread2.start()
    print("recv thread started")
    print("init done")

init_conn()

root.mainloop()
