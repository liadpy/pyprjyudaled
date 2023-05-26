import math
import pickle
import socket
import struct
import threading
import secrets
import hashlib
from Crypto.Cipher import AES

from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

semaphore = threading.Semaphore(1)

clients_tuple_list=[]


MAINPORT=1111
IP=socket.gethostbyname(socket.gethostname())
MAIN_ADDRESS=(IP,MAINPORT)
HEADER=64
FORMAT='utf-8'
G=2243 #two big primes
N=1399

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(MAIN_ADDRESS)

vid_intention="vid"

dsa_key = DSA.generate(2048)
dsa_public_key=dsa_key.public_key().export_key()
signer = DSS.new(dsa_key, 'fips-186-3')



def handle_client_thread(conn, addr):
    secretkey=diffie_key_exchange(conn,addr)
    client_public_dsa_key=exchange_dsa_public_keys(conn,addr)
    client_public_dsa_key=DSA.import_key(client_public_dsa_key)


    clients_tuple_list.append((conn, addr,secretkey,client_public_dsa_key))

    verifier = DSS.new(client_public_dsa_key, 'fips-186-3')
    while True:
        intention=recv_msg_from_client(conn,addr)
        if intention:
            if intention ==vid_intention:
                handle_vid_recv_and_send_everyone(conn,addr,secretkey,verifier)




def exchange_dsa_public_keys(conn,addr):
    message_size2 = conn.recv(struct.calcsize("L"))  # getting client's public dsa key
    message_size2 = struct.unpack("L", message_size2)[0]
    data = b""
    while len(data) < message_size2:
        packet = conn.recv(message_size2 - len(data))
        if not packet:
            break
        data += packet
    clientdsa_key = pickle.loads(data)
    print(f"client's public dsa key : {clientdsa_key}")

    #sending my pub dsa key:
    serialized_data = pickle.dumps(dsa_public_key)
    message_size = struct.pack("L", len(serialized_data))  # sending my public dsa key to the server...
    conn.sendall(message_size)
    conn.sendall(serialized_data)
    print(f"server public dsa key : {dsa_public_key}")



    return clientdsa_key



def handle_vid_recv_and_send_everyone(conn, addr,secretkey,verifier):

    message_size = conn.recv(struct.calcsize("L"))
    message_size = struct.unpack("L", message_size)[0]
    data = b""
    while len(data) < message_size:
        packet = conn.recv(message_size - len(data))
        if not packet:
            break
        data += packet
    ciphertuple= pickle.loads(data)#ciphertuple = ( AES(pickle(usr,img)) ,tag ,nounce,signature)
    try:
        hash_obj=SHA256.new(ciphertuple[0])
        verifier.verify(hash_obj,ciphertuple[3])
        print("msg is autintic!!!")
        cipher_dec = AES.new(secretkey, AES.MODE_EAX, ciphertuple[2])
        img_pickled_tuple = cipher_dec.decrypt_and_verify(ciphertuple[0], ciphertuple[1])
        print("got img from the client")
        for i in clients_tuple_list:
            if not (conn in i[0:2] and addr in i[0:2]):  # i != (conn, addr)
                cipher = AES.new(i[2], AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(img_pickled_tuple)

                hash_obj = SHA256.new(ciphertext)
                signature=signer.sign(hash_obj)

                t = (ciphertext, tag, cipher.nonce,signature)
                pt = pickle.dumps(t)
                message_size = struct.pack("L", len(pt))
                semaphore.acquire()
                send_msg_to_client(i[0], i[1], vid_intention)
                i[0].sendall(message_size)
                i[0].sendall(pt)
                print("sent img to the client!")
                semaphore.release()

    except ValueError:
        print("the msg isnt autentic")

def diffie_key_exchange(conn, addr):
    private_y=secrets.randbits(16)   #random 8 bits num
    print(f"private y ={private_y}")
    B=modular_exponentiation(G,private_y,N)
    print(f"B: {B}")
    send_msg_to_client(conn,addr,B)
    a=recv_msg_from_client(conn,addr)
    a=int(a)
    print(f"got a from client {a}")
    secret_key=modular_exponentiation(a,private_y,N)

    #all of this is for converting the shared number from diffie to a 128bit key for the AES
    key_bytes = secret_key.to_bytes(3, byteorder='big', signed=False).rjust(16, b'\x00')#converting to bytestring
    key_padded = key_bytes.rjust(16, b'\x00')
    salt = b'saltvalue'  # Random salt value (keep secret)
    iterations = 1000  # Number of PBKDF2 iterations (choose appropriate value)
    key_128bit = hashlib.pbkdf2_hmac('sha256', key_padded, salt, iterations, dklen=16)
    print(f"MYSECRETE KEY IS {key_128bit}")
    return key_128bit



def send_msg_to_client(conn, addr,msg):
    message = str(msg).encode(FORMAT)  # exchange a,b
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def recv_msg_from_client(conn, addr):
    msg_length = conn.recv(HEADER).decode(FORMAT)  # waiting on this line till i get a msg from the client
    if msg_length:  # if msg not empty
        msg_length = int(msg_length)
        m = conn.recv(msg_length).decode(FORMAT)
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


def listen_to_new_clients():
    s.listen()
    print(f"[SERVER LISTENING ON {IP}]")
    while True:
        conn, addr = s.accept()  # waiting on this line till some1 connects
        thread = threading.Thread(target=handle_client_thread, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE THREADS]......{threading.active_count() - 1} threads/users')

listen_to_new_clients()