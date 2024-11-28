import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.title("Log In to svAIsthi")

def login_page():
    # Load existing credentials from a YAML file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    st.subheader("Login")

    # Add the login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    captcha = st.checkbox("I am not a robot")  # You can replace this with actual captcha if needed

    # Show Login button to trigger authentication
    if st.button('Login'):
        # Check if captcha is selected
        if not captcha:
            st.error('Captcha validation failed. Please confirm you are not a robot.')
            return

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
            fields={"username": username, "password": password},  # Use user input for fields
            captcha=False,  # Since you are using a checkbox as captcha
            single_session=True,  # Only allow one session per user at a time
            clear_on_submit=True,  # Clear inputs after submission
            key='Login',  # Unique key to avoid conflicts
        )

        # Handle login results
        if login_result is not None:
            name, authentication_status, username = login_result

            if authentication_status:
                # Store login status in session_state
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = name
                authenticator.logout('Logout', 'main')
                st.success(f'Welcome *{name}*')

                # Use rerun to trigger a page refresh and go to home.py
                st.experimental_rerun()

            elif authentication_status == False:
                st.error('Incorrect password. Please try again.')

        elif login_result is None:
            # If login_result is None, this indicates either wrong username or captcha failure
            st.error('Incorrect username or captcha. Please try again.')

        # If 'authentication_status' is not found in locals, the user data is missing
        if 'authentication_status' not in locals():
            st.warning('Your account does not exist. Please register.')

# Call the login page function
login_page()
