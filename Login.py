import streamlit as st

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

if st.session_state["current_page"] != "Home":
    st.experimental_set_query_params(page=st.session_state["current_page"])

# Check if session state is initialized
if "users" not in st.session_state:
    st.session_state["users"] = {}  # Store users as a dictionary: {username: password}

st.set_page_config(page_title="Log In", page_icon="🔑")

st.title("Log In to svAIsthi")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Let Me In"):
    users = st.session_state["users"]
    if username in users and users[username] == password:
        st.success("Logged in successfully!")
        st.session_state["authenticated"] = True
        st.session_state["current_page"] = "svAIsthi"
        st.experimental_rerun()
    else:
        st.error("Invalid username or password. Please try again.")
