import streamlit as st



# Check if session state is initialized
if "users" not in st.session_state:
    st.session_state["users"] = {}

st.set_page_config(page_title="Register", page_icon="📝")

st.title("Register for svAIsthi")

new_username = st.text_input("Create a Username")
new_password = st.text_input("Create a Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Sign Me Up"):
    users = st.session_state["users"]
    
    if new_username in users:
        st.error("Username already exists. Please choose a different one.")
    elif new_password != confirm_password:
        st.error("Passwords do not match. Please try again.")
    else:
        users[new_username] = new_password
        st.success("Account created successfully! Please log in.")
        st.session_state["current_page"] = "Login"
        st.experimental_rerun()
