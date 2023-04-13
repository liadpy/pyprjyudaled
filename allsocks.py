from flask import Flask
from flask_socketio import SocketIO,send

def handle_txtmsg(msg):
    print("msg received - "+msg)
    if msg !="user connected":
        send(msg,broadcast=True)