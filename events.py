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

    st.subheader("📋 Event List")

    for _, row in df.iterrows():
        with st.container():
            st.markdown("----")
            st.markdown(f"### {row['EVENT_TITLE']}")

            # Event details as table
            event_details = {
                "Type": row["EVENT_TYPE"],
                "Status": row["EVENT_STATUS"],
                "Location": row["EVENT_LOCATION"],
                "Start Date": row["EVENT_START_DATE"],
                "End Date": row["EVENT_END_DATE"],
                "Women's Event": "Yes" if row.get("EVENT_WOMEN") else "No",
                "Junior Event": "Yes" if row.get("EVENT_JUNIOR") else "No",
                "Veteran Event": "Yes" if row.get("EVENT_VETERAN") else "No",
                "Teams Event": "Yes" if row.get("EVENT_TEAMS") else "No",
            }

            # Display as 2-column table
            for key, value in event_details.items():
                col1, col2 = st.columns([1, 3])
                col1.markdown(f"**{key}**")
                col2.markdown(str(value))

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
