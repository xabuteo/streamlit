import streamlit as st
from utils import get_snowflake_connection

def show():
    if not st.session_state.get("user_email"):
        st.warning("🔒 You must be logged in to view this page.")
        return

    st.title("👤 My Profile")

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

    profile = get_user_profile(st.session_state["user_email"])
    if profile:
        labels = ["First Name", "Last Name", "Date of Birth", "Gender", "Email", "Registered On"]
        for label, value in zip(labels, profile):
            st.write(f"**{label}:** {value}")
    else:
        st.error("Profile not found.")
