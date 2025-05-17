import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def get_initials(first, last):
    return f"{first[0].upper()}{last[0].upper()}"

def show():
    st.title("🙋 My Profile")

    if "user_email" not in st.session_state or not st.session_state["user_email"]:
        st.warning("🔒 Please log in to view your profile.")
        return

    user_email = st.session_state["user_email"]

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT first_name, last_name, date_of_birth, gender, email
            FROM registrations
            WHERE email = %s
        """, (user_email,))
        row = cursor.fetchone()

        if not row:
            st.error("⚠️ No profile found for this user.")
            return

        first_name, last_name, dob, gender, email = row
        initials = get_initials(first_name, last_name)

        # --- Avatar ---
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                    background-color: #3dc2d4;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 36px;
                    margin: 10px auto 20px auto;
                ">{initials}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Profile as vertical table ---
        data = {
            "First Name": first_name,
            "Last Name": last_name,
            "Date of Birth": dob,
            "Gender": gender,
            "Email": email
        }
        df = pd.DataFrame(data.items(), columns=["Field", "Value"])
        st.dataframe(df.set_index("Field"), use_container_width=True, hide_index=False)

        # --- Update Profile Form ---
        with st.expander("✏️ Update Profile"):
            with st.form("update_profile_form"):
                new_first = st.text_input("First Name", first_name)
                new_last = st.text_input("Last Name", last_name)
                new_dob = st.date_input("Date of Birth", dob)
                new_gender = st.selectbox("Gender", ["M", "F", "Other"], index=["M", "F", "Other"].index(gender))

                submitted = st.form_submit_button("Update")
                if submitted:
                    try:
                        cursor.execute("""
                            UPDATE registrations
                            SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s
                            WHERE email = %s
                        """, (new_first, new_last, new_dob.strftime('%Y-%m-%d'), new_gender, user_email))
                        conn.commit()
                        st.success("✅ Profile updated successfully. Please refresh the page.")
                    except Exception as e:
                        st.error(f"❌ Failed to update profile: {e}")

    except Exception as e:
        st.error(f"❌ Error retrieving profile: {e}")
    finally:
        cursor.close()
        conn.close()
