


username = st.text_input("Username")
password = st.text_input("Password", type="password")

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Log In", page_icon="🔑")

st.title("Log In to svAIsthi")


def login_page():
    # Load existing credentials
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        st.error("No users registered. Please register first.")
        return

    st.subheader("Login")

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Login form
    name, authentication_status, username = authenticator.login('Let me in', 'main')

    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.success(f"Welcome, *{name}*!")
        st.title("Main Application Content")
    elif authentication_status == False:
        st.error("Username/password is incorrect")
    elif authentication_status == None:
        st.warning("Please enter your username and password")

