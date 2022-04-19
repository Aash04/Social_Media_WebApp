from flask import Flask, session
from flask import render_template
from flask import request
import os
import sqlite3
from werkzeug.utils import secure_filename

from werkzeug.utils import redirect

app = Flask(__name__, static_url_path='/static')
app.secret_key = "social"

upload_img = 'static/uploads'
allowed_extension = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['upload_img'] = upload_img


@app.route('/')
def homepage():
    return render_template("Welcome.html")


@app.route('/Verify', methods=["Get", "Post"])
def verifyuser():
    if request.method == "POST":
        email = request.form["email"]
        x = email
        password = request.form["pass"]
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select * from SignUp where email=?"
        cur.execute(sql, (x,))
        result = cur.fetchall()
        if result[0][3] == email and result[0][7] == password:
            session['email'] = request.form['email']
            email = session['email']
            con = sqlite3.connect("socialavey.db")
            cur = con.cursor()
            sql = "select Username from SignUp where email=?"
            cur.execute(sql, (email,))
            s = cur.fetchone()[0]
            return render_template("newforyou.html", msg=s)
        else:
            return "Can't Login"
    else:
        return "This will not work"


@app.route('/signup', methods=["Get", "Post"])
def signupPage():
    return render_template('signup.html')


@app.route('/about', methods=["Get"])
def aboutPage():
    return render_template('about.html')


@app.route('/contact', methods=["Get"])
def contactPage():
    return render_template('contact.html')


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
                sql = """INSERT INTO SignUp(name,Lastname,Username, email, Phone, DOB, Address, password, Repassword,
                Gender)VALUES(?,?,?,?,?,?,?,?,?,?); """
                cur.execute(sql, t)
                con.commit()
                msg = "User details successfully registered"

        except:
            con.rollback()
            msg = "Cannot add the user details please try again later"
        finally:
            con.close()
            return render_template("Welcome.html", msg=msg)


@app.route('/newforyou')
def Foryou():
    loggedIn, Name = getLoginDetails()
    with sqlite3.connect('socialavey.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT  Utime,username, msg, image FROM NewPost')
        itemData = cur.fetchall()
    itemData = parse(itemData)
    return render_template("newforyou.html", itemData=itemData, loggedIn=loggedIn, Name=Name)


def files_allowed(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_extension


@app.route('/addpost', methods=["Post"])
def addpost():
    if request.method == "POST":
        message = request.form['msg']
        # Uploading image procedure
        image = request.files['image']

        if 'email' in session:
            email = session['email']
            con = sqlite3.connect("socialavey.db")
            cur = con.cursor()
            sql = "select Username from SignUp where email=?"
            cur.execute(sql, (email,))
            r = cur.fetchall()
            s = r[0][0]
        if image and files_allowed(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['upload_img'], filename))
        imagename = filename
        with sqlite3.connect('socialavey.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO NewPost(username, msg, image) VALUES (?,?,?)''', (s,message, imagename,))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect("/newforyou")


def getLoginDetails():
    with sqlite3.connect('socialavey.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            Name = ''
        else:
            loggedIn = True
            cur.execute("SELECT Username FROM SignUp WHERE email = ?", (session['email'],))
            Name = cur.fetchone()
    conn.close()
    return (loggedIn, Name)


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


@app.route('/SessionLogout')
def logout():
    if 'email' in session:
        session.pop('email', None)
        return render_template('Welcome.html');
    else:
        return '<p>user already logged out</p>'

@app.route('/searchpost',methods=["Post"])
def search1():
    username = request.form["search"]
    con = sqlite3.connect("socialavey.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from NewPost where username=? ", (username,))
    rows = cur.fetchall()
    return render_template("view1.html", rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
