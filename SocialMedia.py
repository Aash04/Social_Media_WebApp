from flask import Flask, session
from flask import render_template
from flask import request
import sqlite3

app = Flask(__name__, static_url_path='/Static')


@app.route('/')
def homepage():
    return render_template("Welcome.html")


@app.route('/Verify', methods=["Get", "Post"])
def verifyuser():
    email = request.form["email"]
    password = request.form["pass"]
    con = sqlite3.connect("socialavey.db")
    cur = con.cursor()
    sql = "select * from SignUp where email=?"
    cur.execute(sql, (email,))
    result = cur.fetchall()
    if result[0][3] == email and result[0][7] == password:
        return render_template('Foryou.html')
    else:
        return "Can't Login"



@app.route('/signup', methods=["Get"])
def signupPage():
    return render_template('signup.html')


@app.route('/AddUserdetails', methods=["Post"])
def adddetails():
    msg = "msg"
    if request.method == "POST":
        try:
            fname = request.form["fname"]
            lname = request.form["lname"]
            uname = request.form["uname"]
            email = request.form["email"]
            phone = request.form["phone"]
            dob = request.form["dob"]
            address = request.form["addr"]
            password = request.form["pass"]
            cnfpassword = request.form["cnfpass"]
            gender = request.form.get("gender")

            t = (fname, lname, uname, email, phone, dob, address, password, cnfpassword, gender)
            with sqlite3.connect("socialavey.db") as con:
                cur = con.cursor()
                sql = """INSERT INTO SignUp(name,Lastname,Username, email, Phone, DOB, Address, password, Repassword,Gender)VALUES(?,?,?,?,?,?,?,?,?,?);"""
                cur.execute(sql, t)
                con.commit()
                msg = "User details successfully registered"

        except:
            con.rollback()
            msg = "Cannot add the user details please try again later"
        finally:
            con.close()
            return render_template("Welcome.html", msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
