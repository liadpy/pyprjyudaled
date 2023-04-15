from flask import Flask, render_template ,redirect , request , url_for,Response,session,flash
from alldb import *
from usrwebcam import *
from allsocks import *
from flask_socketio import SocketIO,send ,emit,join_room,leave_room


app=Flask(__name__) 
app.secret_key="hellothere"
socketio = SocketIO(app,cors_allowed_origins="*")




@app.route('/',methods=["POST","GET"])
def main():
    popupmsg=""
    if "username" in session:
            usr=session["username"]
    else:
        usr="Guest"
    if request.method=="POST":
        if "username" in session:
            if 'crroombtn' in request.form: #check if my btn was clicked...
                roomname = request.form["crroomname"]
                password = request.form["crroompassword"]
                con =add_room_to_db(roomname,password,session["userid"])
                if "nice" in con:
                    return redirect(url_for("room",room=roomname))
                else:
                    popupmsg =con
            elif 'jnroombtn' in request.form:
                roomname = request.form["jnroomname"]
                password = request.form["jnroompassword"]
                con =check_if_can_join_room(roomname,password,session["userid"])
                if "nice" in con:
                    return redirect(url_for("room",room=roomname))
                else:
                    popupmsg =con
        else:
            popupmsg="pls login first"
    return render_template('mainpage.html',username=usr,popupmsg=popupmsg)


@app.route('/<room>',methods=["POST","GET"])
def room(room):
    return render_template("webcamvid.html")



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


@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('message')
def handle_message(message):
    print("\n\ngot the txt msg\n\n "+message)
    emit('get_txt_message', message, broadcast=True)


if __name__ =="__main__":
    socketio.run(app)
    app.run(debug=True)