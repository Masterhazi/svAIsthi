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

# Initialize session state keys
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False  # Default to False

if "username" not in st.session_state:
    st.session_state["username"] = None  # Placeholder for username

# Set page configuration
st.set_page_config(page_title="svAIsthi - Home", page_icon="💊")

st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Sign in", "Sign up"])

if page == "Sign in":
    login_page()
elif page == "Sign up":
    register_page()

