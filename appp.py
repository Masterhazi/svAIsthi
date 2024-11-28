import streamlit as st
from Login import login_page
from Register import register_page
import yaml
from yaml.loader import SafeLoader

# Initialize session state keys
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if "name" not in st.session_state:
    st.session_state["name"] = None

# Set page configuration
st.set_page_config(page_title="svAIsthi - Home", page_icon="💊")

# Home page title and description
st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ["Sign in", "Sign up"])

# Handle navigation
if page == "Sign in":
    login_page()
elif page == "Sign up":
    register_page()

# Redirect to home page if logged in
if st.session_state["logged_in"]:
    st.success(f"Welcome back, {st.session_state['name']}!")
    st.switch_page('home.py')  # Trigger rerun to refresh state or UI
