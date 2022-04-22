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
        sql = "select * from SignUps where email=?"
        cur.execute(sql, (x,))
        result = cur.fetchall()
        if result[0][3] == email and result[0][7] == password:
            session['email'] = request.form['email']
            email = session['email']
            con = sqlite3.connect("socialavey.db")
            cur = con.cursor()
            sql = "select Username from SignUps where email=?"
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
            bio = request.form["bio"]
            t = (fname, lname, uname, email, phone, dob, address, password, cnfpassword, gender, bio)
            with sqlite3.connect("socialavey.db") as con:
                cur = con.cursor()
                sql = """INSERT INTO SignUps(name,Lastname,Username, email, Phone, DOB, Address, password, Repassword,
                Gender,bio)VALUES(?,?,?,?,?,?,?,?,?,?,?); """
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

        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("select username, comment from reaction")
        rows = cur.fetchall()
    itemData = parse(itemData)
    rows = parse(rows)
    return render_template("newforyou.html", itemData=itemData, loggedIn=loggedIn, Name=Name, rows=rows)


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
            sql = "select Username from SignUps where email=?"
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
                cur.execute('''INSERT INTO NewPost(username, msg, image) VALUES (?,?,?)''', (s, message, imagename,))
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
            cur.execute("SELECT Username FROM SignUps WHERE email = ?", (session['email'],))
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


@app.route('/searchpost', methods=["Post"])
def search1():
    username = request.form["search"]
    con = sqlite3.connect("socialavey.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from NewPost where username=? ", (username,))
    rows = cur.fetchall()
    return render_template("view1.html", rows=rows)


@app.route('/addcomment', methods=["Post"])
def comment():
    if request.method == "POST":
        comment = request.form["comment"]
        if 'email' in session:
            email = session['email']
            con = sqlite3.connect("socialavey.db")
            cur = con.cursor()
            sql = "select Username from SignUps where email=?"
            cur.execute(sql, (email,))
            r = cur.fetchall()
            x = r[0][0]
        with sqlite3.connect('socialavey.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO reaction(username, comment) VALUES (?,?)''', (x, comment,))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect("/newforyou")


@app.route('/Profile')
def viewprofile():
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select Username from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        x = r[0][0]
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select name,Lastname from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        s = r[0]
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select DOB from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        d = r[0][0]
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select bio from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        b = r[0][0]
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select Address from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        a = r[0][0]
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select Gender from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        g = r[0][0]
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select Username from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        y = r[0][0]

        cur = con.cursor()
        sql1 = "SELECT COUNT(*) AS total FROM NewPost WHERE username=?"
        cur.execute(sql1, (y,))
        r = cur.fetchall()
        c = r[0][0]
    return render_template("UserProfile.html", msg=x, name=s, dob=d, bio=b, addr=a, gen=g, count=c)


@app.route('/Chat')
def socialchat():
    return redirect("http://127.0.0.1:8000/")


@app.route('/editusername')
def edituser():
    return render_template('edit.html')


@app.route('/Editusername', methods=["Post"])
def useredit():
    if 'email' in session:
        email = session['email']
        user = request.form["nuser"]
        t = (user, email)
    d = sqlite3.connect("socialavey.db")
    with d as con:
        try:
            cur = con.cursor()
            cur.execute("update SignUps set Username=? where email=?", t)
            con.commit()
            return redirect('/Profile')
        except:
            con.rollback()


@app.route('/editbio')
def editbio():
    return render_template('edit2.html')


@app.route('/Editbio', methods=["Post"])
def bioedit():
    if 'email' in session:
        email = session['email']
        bio = request.form["nbio"]
        t = (bio, email)
    d = sqlite3.connect("socialavey.db")
    with d as con:
        try:
            cur = con.cursor()
            cur.execute("update SignUps set bio=? where email=?", t)
            con.commit()
            return redirect('/Profile')
        except:
            con.rollback()


@app.route('/editdob')
def editdob():
    return render_template('edit3.html')


@app.route('/Editdob', methods=["Post"])
def dobedit():
    if 'email' in session:
        email = session['email']
        dob = request.form["ndob"]
        t = (dob, email)
    d = sqlite3.connect("socialavey.db")
    with d as con:
        try:
            cur = con.cursor()
            cur.execute("update SignUps set DOB=? where email=?", t)
            con.commit()
            return redirect('/Profile')
        except:
            con.rollback()


@app.route('/editpass')
def editpass():
    return render_template('edit4.html')


@app.route('/Editpass', methods=["Post"])
def passedit():
    if 'email' in session:
        email = session['email']
        passw = request.form["npass"]
        cnfpassw = request.form["cnfnpass"]
        t = (passw, cnfpassw, email)
    d = sqlite3.connect("socialavey.db")
    with d as con:
        try:
            cur = con.cursor()
            cur.execute("update SignUps set password=?,Repassword=? where email=?", t)
            con.commit()
            return redirect('/Profile')
        except:
            con.rollback()


@app.route('/deletepost')
def dele():
    if 'email' in session:
        email = session['email']
        con = sqlite3.connect("socialavey.db")
        cur = con.cursor()
        sql = "select Username from SignUps where email=?"
        cur.execute(sql, (email,))
        r = cur.fetchall()
        x = r[0][0]

        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from NewPost where username=?", (x,))
        rows = cur.fetchall()
        return render_template("delete.html", rows=rows)


@app.route('/delpost', methods=["Post"])
def del1():
    pid = request.form["del"]
    with sqlite3.connect("socialavey.db") as con:
        try:
            cur = con.cursor()
            cur.execute("delete from NewPost where pid=?", (pid,))

        except:
            con.rollback()

        finally:
            return redirect('/deletepost')


if __name__ == '__main__':
    app.run(debug=True)
