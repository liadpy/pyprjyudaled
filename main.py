from flask import Flask, render_template ,redirect , request , url_for,Response,session
from alldb import *
from usrwebcam import *

app=Flask(__name__) 
app.secret_key="hellothere"

@app.route('/',methods=["POST","GET"])
def main():
    if "username" not in session:
        usr="Guest"
    else:
        usr=session["username"]
    return render_template('mainpage.html',username=usr)



@app.route('/video',methods=["POST","GET"])
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')




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





if __name__ =="__main__":
    app.run(debug=True)