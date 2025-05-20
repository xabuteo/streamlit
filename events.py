import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("📅 Events")

    # Initialize session state for selected event
    if "selected_event_id" not in st.session_state:
        st.session_state.selected_event_id = None

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

    # Filter/search section
    st.subheader("🔍 Search and Filter")

    col1, col2, col3 = st.columns(3)
    with col1:
        title_filter = st.text_input("Search by Title")
    with col2:
        type_filter = st.selectbox("Event Type", options=["All"] + sorted(df["EVENT_TYPE"].dropna().unique().tolist()))
    with col3:
        status_filter = st.selectbox("Event Status", options=["All"] + sorted(df["EVENT_STATUS"].dropna().unique().tolist()))

    # Apply filters
    if title_filter:
        df = df[df["EVENT_TITLE"].str.contains(title_filter, case=False, na=False)]
    if type_filter != "All":
        df = df[df["EVENT_TYPE"] == type_filter]
    if status_filter != "All":
        df = df[df["EVENT_STATUS"] == status_filter]

    # Drop hidden columns
    hidden_cols = ["ID", "ASSOCIATION_ID", "EVENT_COMMENTS", "REG_OPEN_DATE", "REG_CLOSE_DATE", "EVENT_EMAIL"]
    df_display = df.drop(columns=[col for col in hidden_cols if col in df.columns])

    # Handle event selection
    def select_event(event_id):
        st.session_state.selected_event_id = event_id
        st.session_state.page = "Event Details"
        st.rerun()

    # Show filtered events with clickable titles
    st.subheader("📋 Event List")
    for _, row in df_display.iterrows():
        with st.container():
            st.markdown(f"### {row['EVENT_TITLE']}")
            meta = f"📍 {row['EVENT_LOCATION']} | 🕒 {row['EVENT_START_DATE']} → {row['EVENT_END_DATE']}"
            st.markdown(meta)
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                st.button("View Details", key=f"view_{row['ID']}", on_click=select_event, args=(row['ID'],))
            st.markdown("---")

    # Add new event form (optional)
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
