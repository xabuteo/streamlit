import streamlit as st
import streamlit_authenticator as stauth
import yaml

# Import your pages here
import home
import my_clubs
import club_requests
import events
import my_profile

from auth import load_credentials  # Auth loader with DB + YAML merge

# --- Set page config immediately ---
st.set_page_config(page_title="Xabuteo App", layout="wide")

# --- Auth setup ---

credentials = load_credentials()

authenticator = stauth.Authenticate(
    credentials['credentials'],
    credentials['cookie']['name'],
    credentials['cookie']['key'],
    cookie_expiry_days=credentials['cookie']['expiry_days']
)

# --- Main app ---

def main():
    with st.sidebar:
        name, authentication_status, username = authenticator.login("Login", "sidebar")

    if authentication_status:
        st.sidebar.write(f"Welcome, **{name}**")
        if st.sidebar.button("Logout"):
            authenticator.logout("Logout", "sidebar")
            st.experimental_rerun()

        pages = {
            "Home": home.show,
            "My Clubs": my_clubs.show,
            "Club Requests": club_requests.show,
            "Events": events.show,
            "My Profile": my_profile.show,
        }

        st.sidebar.markdown("---")
        selection = st.sidebar.radio("Navigation", list(pages.keys()))

        pages[selection]()

    elif authentication_status is False:
        st.error("❌ Username/password is incorrect")
    else:
        st.info("👋 Please enter your username and password")

if __name__ == "__main__":
    main()
