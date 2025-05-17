import streamlit as st
import home, register, login, profile, my_clubs

st.set_page_config(page_title="Xabuteo", layout="wide")

if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

st.sidebar.title("Xabuteo")

# Navigation options
if st.session_state["user_email"]:
    selection = st.sidebar.radio("Navigation", ["Home", "My Profile", "My Clubs", "Logout"])
else:
    selection = st.sidebar.radio("Navigation", ["Home", "Register", "Login"])

# Page routing
if selection == "Home":
    home.show()
elif selection == "Register":
    register.show()
elif selection == "Login":
    login.show()
elif selection == "My Profile":
    profile.show()
elif selection == "My Clubs":
    my_clubs.show()
elif selection == "Logout":
    st.session_state["user_email"] = None
    st.rerun()
