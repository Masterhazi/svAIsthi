import streamlit as st
from Login import login_page
from Register import register_page
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import re
from googleapiclient.discovery import build
import requests
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader



st.set_page_config(page_title="svAIsthi - Home", page_icon="💊")

st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

if 'logged_in' in st.session_state and st.session_state.logged_in:
    import home  # If logged in, load the home page
else:
    # Otherwise, show the login or register options
    st.title("Welcome to svAIsthi")
    page = st.sidebar.selectbox("Choose a page", ["Login", "Register"])

    if page == "Login":
        import login  # If login is selected, load the login page
    elif page == "Register":
        import register  # If register is selected, load the register page

