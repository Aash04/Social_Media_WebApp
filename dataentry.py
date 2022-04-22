import sqlite3
con=sqlite3.connect("socialavey.db")
cursor=con.cursor()
q1="delete from NewPost where pid=3;"
cursor.execute(q1)
con.commit()