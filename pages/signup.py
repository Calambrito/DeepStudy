import streamlit as st
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

def verify_signup(username, password, courses):
    if username == "" or password == "":
        st.error("Username or password cannot be empty.")
        return False
    
    if courses == []:
        st.error("You must select atleast one course.")
        return False

    cursor.execute(f"SELECT * FROM USERS WHERE username = '{username}'")
    row = cursor.fetchone()

    if row == None:
        st.session_state['username'] = username
        cursor.execute(f"INSERT INTO USERS VALUES('{username}', '{password}')")
        for course in courses:
            cursor.execute(f"INSERT INTO USERCOURSES VALUES('{username}', '{course}')")
        conn.commit()
        return True
    
    st.error("Username already in use.")
    return False

st.write("")
with st.form(key = "Login"):
    username = st.text_input("Enter your username: ")
    password = st.text_input("Enter your password: ", type="password")
    courses = st.multiselect(
        "What courses would you like to add to your planner?",
        ["CSE115", "CSE173", "CSE215", "CSE225", "CSE231", "CSE325", "CSE331", "CSE332", "CSE373"],
    )
    login_button = st.form_submit_button("Sign Up")

st.page_link("login.py",label="Log In")

if login_button:
    if verify_signup(username, password, courses):
        st.switch_page("pages/app.py")
        
conn.close()