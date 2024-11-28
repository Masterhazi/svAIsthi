import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Log In", page_icon="🔑")

st.title("Log In to svAIsthi")

def login_page():
    # Load existing credentials from a YAML file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    st.subheader("Login")
    
    # Set up the authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Call login() method with appropriate parameters
    login_result = authenticator.login(
        location='main',  # The form will be rendered in the main area
        max_concurrent_users=None,  # No limit on concurrent logins
        max_login_attempts=3,  # Maximum of 3 login attempts before blocking
        fields={"username": "Username", "password": "Password"},  # Custom field names
        captcha=True,  # Enable captcha to prevent bots
        single_session=True,  # Only allow one session per user at a time
        clear_on_submit=True,  # Clear inputs after submission
        key='Login',  # Unique key to avoid conflicts
    )

    if login_result is not None:
        name, authentication_status, username = login_result

        if authentication_status:
            authenticator.logout('Logout', 'main')
            st.write(f'Welcome *{name}*')
            st.title('Some content')
        elif authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication_status == None:
            st.warning('Please enter your username and password')
    else:
        st.error('Login failed. Please try again.')
