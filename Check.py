import sqlite3
con=sqlite3.connect("socialavey.db")
cursor=con.cursor()
q1= "select * from SignUp"
cursor.execute(q1)

result = cursor.fetchall()
print(result)
con.close()