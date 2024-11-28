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


st.set_page_config(
    page_title="💊 svAIsthi",
    page_icon="https://github.com/Masterhazi/svAIsthi/blob/main/health-8.ico",
)

st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Sign in", "Sign up"])

if page == "Sign in":
    login_page()
elif page == "Sign up":
    register_page()
