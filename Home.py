import streamlit as st
from Login import Login
from Register import Register


st.set_page_config(page_title="svAIsthi - Home", page_icon="💊")

st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Login", "Register"])

if page == "Login":
    login_page()
elif page == "Register":
    register_page()

