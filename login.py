import streamlit as st
import sqlite3
from pdfbuilder import *
from populate import populate_db

conn = sqlite3.connect("users.db", check_same_thread=False)
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
        with st.spinner("Retrieving your data"):
            schedule = parse_schedule("rawdata/schedule.txt")
            update_sieve_courses(st.session_state['username'], "rawdata/sieve.txt")
            sieve_courses = get_sieve_courses("rawdata/sieve.txt")
            filtered_schedule = filter_schedule(schedule, sieve_courses)
            build_pdf(filtered_schedule, "data/filtered_schedule.pdf")
            populate_db()

        st.switch_page("pages/app.py")

conn.close()