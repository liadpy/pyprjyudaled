import mysql.connector
import string

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
                return True
        db.close()
        return False
    db.close()    
    return False



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
            print(i)
            if username in i or password in i:
                print("no sucsses")
                return False
        c.execute(f"""INSERT INTO users (username,password) 
        VALUES ('{username}', '{password}');""")           #if user dosent exists... insert
        db.commit()  # save
        db.close()
        return True
    print("no sucsses")
    return False


        
