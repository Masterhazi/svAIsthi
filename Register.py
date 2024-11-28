import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader



st.title("Register for svAIsthi")

def register_page():
    # Load existing credentials
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Initialize config if the file does not exist
        config = {
            'credentials': {
                'usernames': {}
            },
            'cookie': {
                'name': 'auth_cookie',
                'key': 'random_key',
                'expiry_days': 30
            }
        }

    st.subheader("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign me up"):
        if username in config['credentials']['usernames']:
            st.error("Username already exists. Please choose a different username.")
        elif any(user.get('email') == email for user in config['credentials']['usernames'].values()):
            st.error("Email already registered. Please use a different email.")
        else:
            hashed_password = stauth.Hasher([password]).hash()[0]
            new_user = {
                "name": username,
                "email": email,
                "password": hashed_password
            }
            config['credentials']['usernames'][username] = new_user

            # Save updated credentials to config.yaml
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)

            st.success("User registered successfully! Please log in.")
            st.experimental_rerun()

