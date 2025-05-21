import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("📅 Events")

    # Load events
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM xabuteo.public.events_v ORDER BY EVENT_START_DATE DESC")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
    except Exception as e:
        st.error(f"Error loading events: {e}")
        return
    finally:
        cursor.close()
        conn.close()

    if df.empty:
        st.info("No events found.")
        return

    # Filters
    st.subheader("🔍 Search and Filter")
    col1, col2, col3 = st.columns(3)

    with col1:
        title_filter = st.text_input("Search by Title")

    with col2:
        type_filter = st.selectbox(
            "Event Type",
            options=["All"] + sorted(df["EVENT_TYPE"].dropna().unique().tolist()) if "EVENT_TYPE" in df.columns else ["All"]
        )

    with col3:
        status_filter = st.selectbox(
            "Event Status",
            options=["All"] + sorted(df["EVENT_STATUS"].dropna().unique().tolist()) if "EVENT_STATUS" in df.columns else ["All"]
        )

    # Apply filters
    if title_filter and "EVENT_TITLE" in df.columns:
        df = df[df["EVENT_TITLE"].str.contains(title_filter, case=False, na=False)]
    if type_filter != "All" and "EVENT_TYPE" in df.columns:
        df = df[df["EVENT_TYPE"] == type_filter]
    if status_filter != "All" and "EVENT_STATUS" in df.columns:
        df = df[df["EVENT_STATUS"] == status_filter]

    # Columns to hide
    hide_cols = {
        "ID", "ASSOCIATION_ID", "EVENT_COMMENTS", "REG_OPEN_DATE", "REG_CLOSE_DATE", "EVENT_EMAIL"
    }
    display_cols = [col for col in df.columns if col not in hide_cols]
    df_display = df[display_cols]

    st.subheader("📋 Event List")
    st.dataframe(df_display, use_container_width=True)

    # Add new event
    with st.expander("➕ Add New Event"):
        with st.form("add_event_form"):
            title = st.text_input("Event Title")
            event_type = st.text_input("Event Type")
            location = st.text_input("Location")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            status = st.selectbox("Event Status", ["Pending", "Confirmed", "Cancelled"])
            submit = st.form_submit_button("Add Event")

            if submit:
                try:
                    conn = get_snowflake_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO xabuteo.public.events (
                            event_title, event_type, event_location, event_start_date, event_end_date, event_status
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        title, event_type, location,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        status
                    ))
                    conn.commit()
                    st.success("✅ Event added successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error inserting event: {e}")
                finally:
                    cursor.close()
                    conn.close()
