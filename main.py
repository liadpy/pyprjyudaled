from flask import Flask, render_template ,redirect , request , url_for,Response
from alldb import *
from usrwebcam import *

app=Flask(__name__) 


@app.route('/',methods=["POST","GET"])
def main():
    return render_template('mainpage.html')



@app.route('/video',methods=["POST","GET"])
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')





@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form["usrnamelogin"]
        password=request.form["pwlogin"]
        con = loginusr(password,username)
        if con:
            return redirect(url_for('main'))
        else:
            return f"<h3>username or password invalid</h3>"       
    else:
        return render_template('loginpage.html')
    






@app.route('/register',methods=["POST","GET"])
def register():
    if request.method=="POST":
        username=request.form["usrnamereg"]
        password=request.form["pwreg"]
        con = registerusr(password,username)
        if con==True:
            return redirect(url_for('main'))
        else:
            return f"<h3>try other password or username</h3>"       
    else:
        return render_template('registerpage.html')





if __name__ =="__main__":
    app.run(debug=True)