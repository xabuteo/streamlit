import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("🎯 Event Details")

    event_id = st.session_state.get("selected_event_id")
    if not event_id:
        st.warning("No event selected.")
        return

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM xabuteo.public.events_v WHERE id = %s", (event_id,))
        row = cursor.fetchone()
        cols = [desc[0] for desc in cursor.description]

        if not row:
            st.warning("Event not found.")
            return

        df = pd.DataFrame([row], columns=cols).transpose()
        df.reset_index(inplace=True)
        df.columns = ["Field", "Value"]

        st.dataframe(df, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading event details: {e}")
    finally:
        cursor.close()
        conn.close()

    if st.button("⬅️ Back to Events"):
        st.session_state.selected_event_id = None
        st.session_state.page = "Events"
        st.rerun()
