import streamlit as st

# Import page modules
import home
import register
import login
import my_profile
import my_clubs
import club_requests
import events

st.set_page_config(page_title="Xabuteo", layout="wide", initial_sidebar_state="expanded")

# --- Initialize session state ---
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# --- Define page options dynamically ---
pages = {
    "Home": home.show,
}

if st.session_state["user_email"]:
    # Logged-in user options
    pages.update({
        "My Profile": my_profile.show,
        "My Clubs": my_clubs.show,
        "Club Requests": club_requests.show,
        "Events": events.show,
        "Logout": lambda: logout()
    })
else:
    # Anonymous user options
    pages.update({
        "Register": register.show,
        "Login": login.show
    })

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 📋 Xabuteo Menu")
    selection = st.radio("Navigate to", list(pages.keys()), label_visibility="collapsed")

# --- Page Routing ---
def logout():
    st.session_state["user_email"] = None
    st.success("✅ Logged out.")
    st.rerun()

# Render selected page
pages[selection]()
