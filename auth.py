import yaml
from utils import get_snowflake_connection

def load_config_yaml():
    with open('config.yaml') as file:
        return yaml.safe_load(file)

def fetch_db_users():
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, first_name || ' ' || last_name AS name, password
        FROM registrations
        WHERE password IS NOT NULL
    """)
    rows = cursor.fetchall()
    users = {}
    for email, name, password in rows:
        users[email] = {
            "name": name,
            "email": email,
            "password": password
        }
    cursor.close()
    conn.close()
    return users

def merge_users(yaml_users, db_users):
    combined = yaml_users.copy()
    combined.update(db_users)  # DB users override YAML if duplicate
    return combined

def load_credentials():
    config = load_config_yaml()
    yaml_users = config['credentials']['usernames']
    db_users = fetch_db_users()
    merged_users = merge_users(yaml_users, db_users)
    config['credentials']['usernames'] = merged_users
    return config
