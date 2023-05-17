import mysql.connector
import string
import datetime

def check_if_can_join_room(roomname,password,usrid):
    if check_if_input_ok_for_db(roomname) and check_if_input_ok_for_db(password):
        db=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="meshpuk2133meshpuk2133",
        database="medb"
        )
        c=db.cursor() #cursor is like something that allows me to do things with the database /////id room_name room_password user_opened time_opened connected_users
        c.execute("CREATE DATABASE IF NOT EXISTS medb")
        c.execute("""CREATE TABLE IF NOT EXISTS rooms(
                      id INT AUTO_INCREMENT PRIMARY KEY,
                       roomname VARCHAR(50) NOT NULL,
                       roompassword VARCHAR(50) NOT NULL,
                       userid_opened VARCHAR(50) NOT NULL,
                       time_opened VARCHAR(50) NOT NULL,
                       date_opened DATE NOT NULL ,
                       connected_users VARCHAR(50) NOT NULL,
                       status VARCHAR(50) NOT NULL
                        );""")
        c.execute("SELECT * FROM rooms")
        x=c.fetchall()
        for i in x:
            if(roomname in i and password in i and i[-1]=="open"):
                c.execute(f"""UPDATE rooms SET connected_users = CONCAT(connected_users, '{usrid},') WHERE roomname='{roomname}' and roompassword='{password}' ;""")
                db.commit()
                db.close()
                return "nice"
    return str.lower("room not found :(   make sure you have the correct password and the correct roomname")



def add_room_to_db(roomname,password,usrid):
    if check_if_input_ok_for_db(roomname) and check_if_input_ok_for_db(password):
        db=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="pw",
        database="medb"
        )
        c=db.cursor() #cursor is like something that allows me to do things with the database /////id room_name room_password user_opened time_opened connected_users
        c.execute("CREATE DATABASE IF NOT EXISTS medb")
        c.execute("""CREATE TABLE IF NOT EXISTS rooms(
                      id INT AUTO_INCREMENT PRIMARY KEY,
                       roomname VARCHAR(50) NOT NULL,
                       roompassword VARCHAR(50) NOT NULL,
                       userid_opened VARCHAR(50) NOT NULL,
                       time_opened VARCHAR(50) NOT NULL,
                       date_opened DATE NOT NULL ,
                       connected_users VARCHAR(50) NOT NULL,
                       status VARCHAR(50) NOT NULL
                        );""")
        c.execute("SELECT * FROM rooms")
        x=c.fetchall()
        for i in x:
            if(roomname in i and password in i):
                return "this room already exists try other room name or password"
        current_time = datetime.datetime.now().time()
        time = current_time.strftime('%H:%M:%S')
        current_date = datetime.date.today()
        date = current_date.strftime("%d-%m-%Y")
        date=fix_date(date)
        c.execute(f"""INSERT INTO rooms (roomname,roompassword,userid_opened,time_opened,date_opened,connected_users,status) 
        VALUES ('{roomname}', '{password}','{usrid}','{time}','{date}','{usrid},','open');""")#TODO remember to change closed to "open" later
        db.commit()  # save
        db.close()
        return "nice",
    return str.lower("MAKE SURE THAT YOUR ROOMNAME AND PASSWORD HAS NO SPACES AND NO SYMBOLS")
        

       
        
        
def fix_date(date): #need to exchange year and day for db
    l=date.split('-')
    l[0],l[-1]=l[-1],l[0]
    return "-".join(l)


def check_if_input_ok_for_db(inpt):
    if inpt == "":
        return False
    for i in inpt:
        if i not in string.ascii_letters and i not in string.digits:
            return False
    return True

def loginusr(password,username):
    if check_if_input_ok_for_db(username) and check_if_input_ok_for_db(password):
        db=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="meshpuk2133meshpuk2133",
        database="medb"
        )
        c=db.cursor() #cursor is like something that allows me to do things with the database
        c.execute("CREATE DATABASE IF NOT EXISTS medb")
        c.execute("""CREATE TABLE IF NOT EXISTS users(
                      id INT AUTO_INCREMENT PRIMARY KEY,
                       username VARCHAR(50) NOT NULL,
                       password VARCHAR(50) NOT NULL
                        );""")
        c.execute("SELECT * FROM users")  #checking if user exists...
        x = c.fetchall()
        for i in x:
            if username in i and password in i:
                db.close()
                return i
        db.close()
        return []
    return []



def registerusr(password , username):
    if check_if_input_ok_for_db(username) and check_if_input_ok_for_db(password):
        db=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="meshpuk2133meshpuk2133",
        database="medb"
        )
        c=db.cursor() #cursor is like something that allows me to do things with the database
        c.execute("CREATE DATABASE IF NOT EXISTS medb")
        c.execute("""CREATE TABLE IF NOT EXISTS users(
                      id INT AUTO_INCREMENT PRIMARY KEY,
                       username VARCHAR(50) NOT NULL,
                       password VARCHAR(50) NOT NULL
                        );""")
        c.execute("SELECT * FROM users")  #checking if user exists...
        x = c.fetchall()
        for i in x:
            if username in i or password in i:
                return []
        c.execute(f"""INSERT INTO users (username,password) 
        VALUES ('{username}', '{password}');""")           #if user dosent exists... insert
        c.execute(f"SELECT * FROM users where username = '{username}' and password= '{password}'")
        i=c.fetchone()
        db.commit()  # save
        db.close()
        return i
    return []


        
