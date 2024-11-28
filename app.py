import streamlit as st
from Login import login_page
from Register import register_page
from home import home_page  # Import the home page function
import os
from dotenv import load_dotenv

st.set_page_config(page_title="svAIsthi - Home", page_icon="💊")

st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

# Sidebar for navigation
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False  # Set default login status to False

if st.session_state["logged_in"]:
    home_page()  # If logged in, show the home page
else:
    page = st.sidebar.selectbox("Choose a page", ["Sign in", "Sign up"])

    if page == "Sign in":
        login_page()  # Show the login page if "Sign in" is selected
    elif page == "Sign up":
        register_page()  # Show the registration page if "Sign up" is selected
