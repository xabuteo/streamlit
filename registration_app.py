import streamlit as st
import snowflake.connector
import uuid
from datetime import datetime
import bcrypt

# ------------------ SNOWFLAKE CONNECTION CONFIG ------------------
SNOWFLAKE_CONFIG = {
    'user': 'YOUR_USER',
    'password': 'YOUR_PASSWORD',
    'account': 'YOUR_ACCOUNT',
    'warehouse': 'YOUR_WAREHOUSE',
    'database': 'YOUR_DATABASE',
    'schema': 'YOUR_SCHEMA'
}

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_CONFIG['user'],
        password=SNOWFLAKE_CONFIG['password'],
        account=SNOWFLAKE_CONFIG['account'],
        warehouse=SNOWFLAKE_CONFIG['warehouse'],
        database=SNOWFLAKE_CONFIG['database'],
        schema=SNOWFLAKE_CONFIG['schema']
    )

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode('utf-8')

def insert_registration(data):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT COUNT(*) FROM registrations WHERE email = %s", (data['email'],))
        if cursor.fetchone()[0] > 0:
            st.warning("🚫 This email is already registered.")
            return False

        cursor.execute("""
            INSERT INTO registrations (id, first_name, last_name, date_of_birth, gender, email, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            data['first_name'],
            data['last_name'],
            data['date_of_birth'].strftime('%Y-%m-%d'),
            data['gender'],
            data['email'],
            hash_password(data['password'])
        ))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving to Snowflake: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# ------------------ STREAMLIT UI ------------------

st.set_page_config(page_title="Xabuteo", layout="wide")

# Sidebar Navigation
with st.sidebar:
    st.title("☰ Menu")
    selected_page = st.radio("Navigate", ["Home", "Register"])

# Home Page
if selected_page == "Home":
    st.title("🏠 Welcome to Xabuteo")
    st.markdown("""
        **Xabuteo website.**  
        Complete registration to gain access to the site content.
    """)

# Registration Page
elif selected_page == "Register":
    st.title("📝 User Registration")
    with st.form("registration_form"):
        st.subheader("Enter your details:")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        date_of_birth = st.date_input("Date of Birth")
        gender = st.selectbox("Gender", ["M", "F", "Other"])
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register")
        if submitted:
            if all([first_name, last_name, email, password]):
                form_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "gender": gender,
                    "email": email,
                    "password": password
                }
                if insert_registration(form_data):
                    st.success("🎉 Registration successful!")
            else:
                st.warning("Please fill in all required fields.")
