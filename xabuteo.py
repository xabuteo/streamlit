# xabuteo.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pages import register, login, my_profile, my_clubs, club_requests, events

# Load configuration for authentication
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.success(f"Welcome {name}!")
    authenticator.logout("Logout", "sidebar")

    st.sidebar.title("Navigation")
    pages = {
        "Home": lambda: st.write("# 🏠 Xabuteo Website\nComplete registration to gain access to the site content."),
        "My Profile": my_profile.show,
        "My Clubs": my_clubs.show,
        "Club Requests": club_requests.show,
        "Events": events.show
    }
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    pages[selection]()

elif authentication_status is False:
    st.error("Username or password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")

# Allow registration page to be accessed separately
if not authentication_status:
    st.sidebar.markdown("---")
    if st.sidebar.button("Register"):
        register.show()
