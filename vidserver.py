import socket
import struct
import threading


clients_tuple_list=[]
client_tuple_audio_list = []


vidintentionmsg="vid"
audiointentionmsg="audio"
leaveintentionmsg="leave"

semaphore = threading.Semaphore(1)

MAINPORT=1111                           #video port
AUDIOPORT=1112                          #audio port
IP=socket.gethostbyname(socket.gethostname())
MAIN_ADDRESS=(IP,MAINPORT)              #video port
AUDIO_ADDRESS=(IP,AUDIOPORT)
HEADER=64
FORMAT='utf-8'
DISCONNECT_MSG="!DISCONNECT"

CHUNK = 1024  # Number of audio samples per frame
WIDTH = 2  # Number of bytes per audio sample
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate in Hz

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(MAIN_ADDRESS)                                #vid


sa=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sa.bind(AUDIO_ADDRESS)                                #audio

def get_encodedsize(msg):
    if type(msg)=='bytes':
        message = msg.encode(FORMAT)
    else:
        message = msg
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    return send_length

def handle_client(conn,addr):       #addr is the ip+port of the client ||| conn is the socket of the client
    print(f"[NEW THREAD]......addr:{addr} ,conn:{conn}connected")
    clients_tuple_list.append((conn,addr))
    connected=True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)  # waiting on this line till i get a msg from the client
        if msg_length:  # if msg not empty
            msg_length = int(msg_length)
            intention = conn.recv(msg_length).decode(FORMAT)
            if intention == vidintentionmsg:
                handle_client_vid(conn,addr)
            elif intention == leaveintentionmsg:
                dissconnect_user(conn,addr)
                break



def dissconnect_user(conn,addr):
    clients_tuple_list.remove((conn,addr))
    for i in client_tuple_audio_list:
        if addr[0] in i[-1]:
            client_tuple_audio_list.remove(i)
            i[0].close
    conn.close
    print(f"{addr} closed")


def handle_client_vid(conn,addr):
    message_size = conn.recv(struct.calcsize("L"))
    message_size = struct.unpack("L", message_size)[0]
    data = b""
    while len(data) < message_size:
        packet = conn.recv(message_size - len(data))
        if not packet:
            break
        data += packet
    for i in clients_tuple_list:
        if (i != (conn, addr)):
            message_size = struct.pack("L", len(data))
            semaphore.acquire()
            i[0].sendall(message_size)
            i[0].sendall(data)
            semaphore.release()



def handle_client_audio(conna, addra):
    print("in handle audio ")
    client_tuple_audio_list.append((conna, addra))

    while True:
        message_size = conna.recv(struct.calcsize("L"))
        message_size = struct.unpack("L", message_size)[0]
        data = b""
        while len(data) < message_size:
            packet = conna.recv(message_size - len(data))
            if not packet:
                break
            data += packet
        for i in client_tuple_audio_list:
            if (i != (conna, addra)):
                message_size = struct.pack("L", len(data))
                semaphore.acquire()
                i[0].sendall(message_size)
                i[0].sendall(data)
                semaphore.release()




def startserver():
    s.listen()
    sa.listen()
    print(f"[SERVER LISTENING ON {IP}]")
    while True:
        conn , addr=s.accept()    #waiting on this line till some1 connects
        thread=threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()
        conna, addra = sa.accept()  # waiting on this line till some1 connects
        threada = threading.Thread(target=handle_client_audio, args=(conna, addra))
        threada.start()
        print(f'[ACTIVE THREADS]......{threading.active_count()-1} threads/users')



print(f"[STARTING_SERVER]......{MAIN_ADDRESS}  server is starting")
startserver()