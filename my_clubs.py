import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("⚽ My Clubs")

    if "user_email" not in st.session_state or not st.session_state["user_email"]:
        st.warning("🔒 Please log in to view your clubs.")
        return

    user_email = st.session_state["user_email"]

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Fetch data
        cursor.execute("SELECT  club_code, club_name, player_status, valid_from, valid_to, email FROM PLAYER_CLUB_V WHERE email = %s", (user_email,))
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        if df.empty:
            st.info("ℹ️ No clubs found for your account.")
            return

        # --- Search ---
        search_query = st.text_input("🔍 Search clubs")

        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        # --- Column filters ---
        with st.expander("🔧 Filter columns"):
            filter_cols = {}
            for col in df.columns:
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) > 1 and len(unique_vals) <= 50:
                    selected_vals = st.multiselect(f"Filter by {col}", options=sorted(unique_vals), default=unique_vals)
                    filter_cols[col] = selected_vals

            for col, selected_vals in filter_cols.items():
                df = df[df[col].isin(selected_vals)]

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error retrieving club data: {e}")
    finally:
        cursor.close()
        conn.close()
