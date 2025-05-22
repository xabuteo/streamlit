import streamlit as st
import streamlit_authenticator as stauth
import yaml

# Import your pages here
import home
import my_clubs
import club_requests
import events
import my_profile

from utils import get_snowflake_connection  # Your DB utils

# --- Auth setup ---

def load_yaml_credentials():
    with open('config.yaml') as file:
        config = yaml.safe_load(file)
    return config['credentials']

def get_db_credentials():
    # Replace with your actual DB call to fetch user credentials
    # Must return dict like {"usernames": {username: {"name": ..., "password": ...}}}
    return {
        "usernames": {
            # example user
            "dbuser1": {
                "name": "DB User One",
                "password": "$2b$12$..."  # bcrypt hashed password string
            }
        }
    }

def get_combined_credentials():
    db_creds = get_db_credentials()
    yaml_creds = load_yaml_credentials()
    combined = {"usernames": {}}
    combined["usernames"].update(db_creds.get("usernames", {}))
    combined["usernames"].update(yaml_creds.get("usernames", {}))
    return combined

credentials = get_combined_credentials()

authenticator = stauth.Authenticate(
    credentials,
    "xabuteo_cookie",  # cookie name
    "xabuteo_signature_key",  # secret key, keep it secret & random!
    cookie_expiry_days=1,
)

# --- Main app ---

def main():
    st.set_page_config(page_title="Xabuteo App", layout="wide")

    # Sidebar login/logout
    with st.sidebar:
        name, authentication_status, username = authenticator.login("Login", "sidebar")

    if authentication_status:
        # Show welcome and logout
        st.sidebar.write(f"Welcome, **{name}**")
        if st.sidebar.button("Logout"):
            authenticator.logout("Logout", "sidebar")
            st.experimental_rerun()

        # Page selection menu in sidebar as radio buttons
        pages = {
            "Home": home.show,
            "My Clubs": my_clubs.show,
            "Club Requests": club_requests.show,
            "Events": events.show,
            "My Profile": my_profile.show,
        }

        st.sidebar.markdown("---")
        selection = st.sidebar.radio("Navigation", list(pages.keys()))

        # Call selected page function
        pages[selection]()

    elif authentication_status is False:
        st.error("❌ Username/password is incorrect")
    else:
        st.info("👋 Please enter your username and password")

if __name__ == "__main__":
    main()
