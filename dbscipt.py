import sqlite3


conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# cursor.execute("CREATE TABLE USERS ('username' VARCHAR(255) PRIMARY KEY, 'password' VARCHAR(255) NOT NULL)")
# cursor.execute("CREATE TABLE USERCOURSES('username' VARCHAR(255) NOT NULL, 'course' VARCHAR(10) NOT NULL)");
# cursor.execute("DELETE FROM USERS")
# cursor.execute("DELETE FROM USERCOURSES")


conn.commit()
conn.close()