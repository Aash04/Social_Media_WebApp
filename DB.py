import sqlite3

con = sqlite3.connect("socialavey.db")

# con.execute("CREATE TABLE SignUp(name varchar(255) ,Lastname varchar(255) ,Username varchar(255) ,email Varchar(255) ,Phone int ,DOB Varchar(255) ,Address varchar(255),password varchar(255),Repassword varchar(255),Gender varchar(255))")

con.execute("CREATE TABLE Posts(pid integer primary key, Utime DATETIME DEFAULT CURRENT_TIMESTAMP, msg text, image text )")

con.close()
