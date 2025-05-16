import streamlit as st
from utils import get_snowflake_connection

st.title("👤 My Profile")

# Simulated session state
if "user_email" not in st.session_state:
    st.warning("🔒 You must be logged in to view this page.")
    st.stop()

email = st.session_state["user_email"]

def get_user_profile(email):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT first_name, last_name, date_of_birth, gender, email, registration_timestamp
            FROM registrations
            WHERE email = %s
        """, (email,))
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Error retrieving profile: {e}")
    finally:
        cursor.close()
        conn.close()

profile = get_user_profile(email)

if profile:
    labels = ["First Name", "Last Name", "Date of Birth", "Gender", "Email", "Registered On"]
    for label, value in zip(labels, profile):
        st.write(f"**{label}:** {value}")
else:
    st.error("Profile not found.")