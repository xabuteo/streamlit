import yaml
import streamlit_authenticator as stauth
from utils import get_snowflake_connection
import bcrypt

def load_config_yaml():
    with open('config.yaml') as file:
        return yaml.safe_load(file)

def fetch_db_users():
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, first_name || ' ' || last_name AS name, password
        FROM registrations
    """)
    rows = cursor.fetchall()
    users = {}
    for email, name, password in rows:
        users[email] = {
            "name": name,
            "email": email,
            "password": password  # Assumes password is already hashed
        }
    cursor.close()
    conn.close()
    return users

def merge_users(yaml_users, db_users):
    combined = yaml_users.copy()
    for username, info in db_users.items():
        if username not in combined:
            combined[username] = info
    return combined

def load_credentials():
    yaml_config = load_config_yaml()
    db_users = fetch_db_users()

    yaml_users = yaml_config['credentials']['usernames']
    merged_users = merge_users(yaml_users, db_users)

    yaml_config['credentials']['usernames'] = merged_users
    return yaml_config
