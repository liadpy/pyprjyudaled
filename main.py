from flask import Flask, render_template ,redirect , request , url_for,session
from alldb import *
from flask_socketio import SocketIO,send ,join_room,leave_room
import socket
#import threading
import subprocess

app=Flask(__name__) 
app.secret_key="hellothere"
socketio = SocketIO(app,cors_allowed_origins="*")
roomdict={}
port=2000
server_file_path="vidserver.py"


@app.route('/',methods=["POST","GET"])
def main():
    if "room" in session:
        session.pop("room",None)
    if request.method=="POST":
        if "username" not in session:
            return render_template('mainpage.html',username="Guest",popupmsg="pls login first")
        if 'crroombtn' in request.form: #check if my btn was clicked...
            roomname = request.form["crroomname"]
            password = request.form["crroompassword"]
            con =add_room_to_db(roomname,password,session["userid"])
            if "nice" in con:
                global port
                roomid=roomname+password
                roomdict[roomid]={"members":0,"msgs":[],"port":port} #creating new mini vidserver
               #thread = threading.Thread(target=listen_to_new_clients, args=(roomdict[roomid]["port"],))
               #thread.start()
                subprocess.Popen(['python', server_file_path, str(port), str(roomname),str(password)])
                port+=1
                session["room"]=roomid
                session["roompassword"]=password
                return redirect(url_for("room",room=roomname))
            else:
                return render_template('mainpage.html',username=session["username"],popupmsg=con)
        elif 'jnroombtn' in request.form:
            roomname = request.form["jnroomname"]
            password = request.form["jnroompassword"]
            con =check_if_can_join_room(roomname,password,session["userid"])
            if "nice" in con:
                session["room"]=roomname+password
                session["roompassword"]=password
                return redirect(url_for("room",room=roomname))
            else:
                render_template('mainpage.html',username=session["username"],popupmsg=con)
    if "username" in session:
        usr=session["username"]
    else:
        usr="Guest"
    return render_template('mainpage.html',username=usr)


@app.route('/<room>',methods=["POST","GET"])
def room(room):#room var is the room name 
    if "room" not in session:
        return redirect(url_for('main'))
    
    return render_template("webcamvid.html",roomname=room,roompassword=session.get("roompassword"),serverip=socket.gethostbyname(socket.gethostname()),port=roomdict[session.get("room")]["port"])



@app.route('/logout',methods=["POST","GET"])
def logout():
    if "username" not in session:
        return redirect(url_for('main'))
    else:
        session.pop("username",None)
        session.pop("userpassword",None)
        session.pop("userid",None)
    return render_template('logout.html',username="Guest")



@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form["usrnamelogin"]
        password=request.form["pwlogin"]
        con = loginusr(password,username)
        if con!=[]:
            session["userid"]=con[0]
            session["username"]=con[1]
            session["userpassword"]=con[2]
            return redirect(url_for('main'))
        else:
            return f"<h3>username or password invalid</h3>"       
    else:
        if "username" not in session:
            usr="Guest"
        else:
            usr=session["username"]
        return render_template('loginpage.html',username=usr)
    


@app.route('/register',methods=["POST","GET"])
def register():
    if request.method=="POST":
        username=request.form["usrnamereg"]
        password=request.form["pwreg"]
        con = registerusr(password,username)
        if con!=[]:
            session["userid"]=con[0]
            session["username"]=con[1]
            session["userpassword"]=con[2]
            return redirect(url_for('main'))
        else:
            return f"<h3>try other password or username</h3>"       
    else:
        if "username" not in session:
            usr="Guest"
        else:
            usr=session["username"]
        return render_template('registerpage.html',username=usr)



@socketio.on("txtmessage")
def txtmessage(data):
    roomid=session.get("room")
    if roomid not in roomdict:
        return
    m={"name":session.get("username"),"message":data["data"]}
    send(m,to=roomid)
    roomdict[roomid]["msgs"].append(m)
    print(f"{session.get('username')} said: {data['data']}")






@socketio.on("connect") # ativates automatically when client creates the socket
def connect(auth):
    roomid=session.get("room")
    usrname=session.get("username")
    if not roomid or not usrname : 
        return
    if roomid not in roomdict:
        leave_room(roomid)
        return
    join_room(roomid)
    send({"name":usrname,"message":" has entered the room"},to=roomid)
    roomdict[roomid]["members"]+=1
    print(f"{usrname} entered room {roomid}")




@socketio.on("disconnect")# ativates automatically when client disconnects
def disconnect():
    roomid = session.get("room")
    username = session.get("username")
    leave_room(roomid)

    if room in roomdict:
        roomdict[roomid]["members"] -= 1
        if roomdict[roomid]["members"] <= 0:
            del roomdict[roomid]
    
    send({"name": username, "message": "has left the room"}, to=roomid)
    print(f"{username} has left the room {roomid}")


if __name__ =="__main__":
    socketio.run(app,debug=True)
    app.run(debug=True)