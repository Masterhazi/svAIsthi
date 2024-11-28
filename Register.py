import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Title for the registration page
st.title("Register for svAIsthi")

def register_page():
    try:
        # Load existing credentials from config.yaml
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Initialize the config if file is not found
        config = {
            'credentials': {
                'usernames': {}
            },
            'cookie': {
                'name': 'auth_cookie',
                'key': 'random_key',
                'expiry_days': 30
            },
            'pre-authorized': []  # Empty list of pre-authorized emails (can be populated later)
        }

    st.subheader("Register User")

    # Define the register_user widget configuration
    try:
        # Use the register_user widget
        email_of_registered_user, username_of_registered_user, name_of_registered_user = stauth.Authenticate(
            config['credentials'], 
            config['cookie']['name'], 
            config['cookie']['key'], 
            config['cookie']['expiry_days']
        ).register_user(
            location='main',  # Registration widget location on the main page
            pre_authorized=config.get('pre-authorized', []),  # Pre-authorized list of emails
            fields={'Form name': 'Register user', 'Email': 'Email', 'Username': 'Username', 
                    'Password': 'Password', 'Repeat password': 'Repeat password', 
                    'Password hint': 'Password hint', 'Captcha': 'Captcha', 'Register': 'Register'},
            captcha=True,  # Enable CAPTCHA for security
            clear_on_submit=True,  # Clear form after submission
            key='Register user',  # Unique key for widget
        )

        # If registration was successful, show success message
        if email_of_registered_user:
            st.success('User registered successfully!')
            st.write(f"Registered Email: {email_of_registered_user}")
            st.write(f"Registered Username: {username_of_registered_user}")
            st.write(f"Registered Name: {name_of_registered_user}")
            # Optionally remove user from the pre-authorized list
            if email_of_registered_user in config['pre-authorized']:
                config['pre-authorized'].remove(email_of_registered_user)

            # Save updated credentials to config.yaml
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)

            # Optionally prompt user to log in or redirect to login page
            st.write("Please log in to continue.")

    except Exception as e:
        st.error(f"Error during registration: {str(e)}")

# Display the registration form
register_page()
