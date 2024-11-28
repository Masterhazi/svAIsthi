import streamlit as st


st.set_page_config(page_title="svAIsthi - Home", page_icon="💊")

st.title("Welcome to svAIsthi")
st.caption("Choose your action below:")

# Navigation buttons
if st.button("Log In"):
    st.session_state["current_page"] = "Login"
    st.experimental_rerun()

if st.button("Register"):
    st.session_state["current_page"] = "Register"
    st.experimental_rerun()
