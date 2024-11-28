import streamlit as st

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

if st.session_state["current_page"] != "Home":
    st.experimental_set_query_params(page=st.session_state["current_page"])


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
