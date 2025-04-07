import streamlit as st
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

def verify_login(username, password):
    cursor.execute(f"SELECT * FROM USERS WHERE username = '{username}'")
    row = cursor.fetchone()

    # st.write(row)
    if row == None:
        st.error("User does not exist")
        return False

    if password == row[1]:
        st.session_state['username'] = username
        return True
    st.error("Incorrect username or password.")
    return False

st.write("")
with st.form(key = "Login"):
    username = st.text_input("Enter your username: ")
    password = st.text_input("Enter your password: ", type="password")
    login_button = st.form_submit_button("Login")

st.page_link("pages/signup.py",label="Sign Up")

if login_button:
    if verify_login(username, password):
        st.switch_page("pages/app.py")

conn.close()