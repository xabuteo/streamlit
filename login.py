import streamlit as st
from utils import get_snowflake_connection, check_password

def show():
    if st.session_state.get("user_email"):
        st.info("🔓 You are already logged in.")
        return

    st.title("🔐 Login")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    def verify_user(email, password):
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM registrations WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                return check_password(password, result[0])
            return False
        except Exception as e:
            st.error(f"Login error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    if st.button("Login"):
        if email and password:
            if verify_user(email, password):
                st.success("✅ Login successful!")
                st.session_state["user_email"] = email
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")
        else:
            st.warning("Please enter both email and password.")
