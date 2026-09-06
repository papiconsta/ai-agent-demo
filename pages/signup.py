import psycopg2
import streamlit as st

from db import DB_CONFIG


def checkIfEmailRegistered(email: str) -> bool:
    """
        Here we fetch the email from the database and check if it is already registered.
    """
    with psycopg2.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cursor.fetchone() is not None

    
def insertToDB(username: str, password: str, surname: str, email: str, age: int) -> None:
    with psycopg2.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, surname, email, age) VALUES (%s, %s, %s, %s, %s)", (username, password, surname, email, age))

with st.form("signup_form"):
    st.header("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    surname = st.text_input("Surname")
    email = st.text_input("Email")
    age = st.number_input("Enter your age", min_value=0, max_value=120, step=1)
    submitted = st.form_submit_button("Sign Up")

    if submitted:
        if checkIfEmailRegistered(email):
            st.error("Email is already registered.")
        elif username and password and surname and email:
            insertToDB(username, password, surname, email, age)
            st.success("Signed up successfully!")
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Please fill in all fields.")