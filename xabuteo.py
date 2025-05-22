import streamlit as st
from streamlit_option_menu import option_menu
from auth import load_credentials
import streamlit_authenticator as stauth

# Import your app pages
import home
import login
import register
import my_profile
import my_clubs
import club_requests
import events

# Load authentication configuration
config = load_credentials()

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days'],
)

import streamlit_authenticator
print(streamlit_authenticator.__version__)

# Perform login
name, auth_status, username = authenticator.login("Login", "main")

# Set session state on successful login
if auth_status:
    st.session_state["user_email"] = username
    st.session_state["user_name"] = name
    authenticator.logout("Logout", "sidebar")
elif auth_status is False:
    st.error("❌ Incorrect username or password.")
elif auth_status is None:
    st.info("🔒 Please log in to continue.")

# Define pages
pages = {
    "Home": home.show,
    "My Profile": my_profile.show,
    "My Clubs": my_clubs.show,
    "Club Requests": club_requests.show,
    "Events": events.show,
    "Login": login.show,
    "Register": register.show
}

# Filter pages based on login status
if st.session_state.get("user_email"):
    available_pages = {
        "Home": home.show,
        "My Profile": my_profile.show,
        "My Clubs": my_clubs.show,
        "Club Requests": club_requests.show,
        "Events": events.show,
    }
else:
    available_pages = {
        "Home": home.show,
        "Login": login.show,
        "Register": register.show
    }

# Show navigation menu as a sidebar radio button
selection = st.sidebar.radio("📂 Navigation", list(available_pages.keys()))
available_pages[selection]()
