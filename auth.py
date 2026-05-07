import streamlit as st
from db import create_user, login_user

def login():
    st.sidebar.subheader("🔐 Account")

    menu = st.sidebar.radio("Select", ["Login", "Signup"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if menu == "Signup":
        if st.sidebar.button("Create Account"):
            success = create_user(username, password)
            if success:
                st.sidebar.success("Account created! Please login.")
            else:
                st.sidebar.error("Username already exists")

    if menu == "Login":
        if st.sidebar.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["user_id"] = user[0]
                st.sidebar.success("Logged in!")
            else:
                st.sidebar.error("Invalid credentials")


def check_auth():
    return "user_id" in st.session_state