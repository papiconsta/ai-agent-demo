import time
from psycopg2.extras import RealDictCursor

import psycopg2
import streamlit as st

from db import DB_CONFIG

def fetchData(username, password):
    with psycopg2.connect(**DB_CONFIG) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            data = cursor.fetchall()
    return data

def checkDB(username, password):
    data = fetchData(username, password)
    if data:
        return True
    else:
        return False

with st.form("login_form"):
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")
    if submitted:
        is_valid = checkDB(username, password)  # Call the checkDB function to validate credentials
        if is_valid:
            data = fetchData(username, password)
            st.session_state["username"] = data[0]["username"]
            st.session_state["user_id"] = data[0]["id"]
            st.session_state["surname"] = data[0]["surname"]
            st.session_state["email"] = data[0]["email"]
            st.session_state["age"] = data[0]["age"]
            st.session_state["previous_conversations"] = []

            st.session_state["logged_in"] = True
            st.toast("Logged in successfully!", icon="✅")
            time.sleep(2)
            st.rerun()
        else:
            st.toast("Invalid username or password.", icon="❌")
    