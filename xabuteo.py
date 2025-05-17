import streamlit as st

# Import your page modules
import home
import register
import login
import my_profile
import my_clubs

st.set_page_config(page_title="Xabuteo", layout="wide", initial_sidebar_state="expanded")

# --- Initialize session state ---
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# --- Define page options dynamically ---
pages = {
    "Home": home.show,
}

if st.session_state["user_email"]:
    # User is logged in
    pages.update({
        "My Profile": my_profile.show,
        "My Clubs": my_clubs.show,
        "Logout": lambda: logout()
    })
else:
    # User not logged in
    pages.update({
        "Register": register.show,
        "Login": login.show
    })

# --- Sidebar Navigation ---
with st.sidebar:
    st.header("Xabuteo")
    selection = st.selectbox("📂 Navigate", list(pages.keys()))

# --- Page Display Logic ---
def logout():
    st.session_state["user_email"] = None
    st.success("✅ Logged out.")
    st.rerun()

# Call the selected page's function
if selection in pages:
    pages[selection]()
