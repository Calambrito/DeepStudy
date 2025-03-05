import streamlit as st
from st_login_form import login_form

client = login_form(allow_guest=False)

attempted = False

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
        st.switch_page("./pages/app.py")
    else:
        st.success("Welcome guest")
else:
    if attempted:
        st.error("Incorrect username or password")

