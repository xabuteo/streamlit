import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("📅 Events")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM xabuteo.public.events_v ORDER BY event_start_date DESC")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)

        if df.empty:
            st.info("No events found.")
            return

        # --- Filters ---
        with st.expander("🔎 Filter Events", expanded=True):
            search_text = st.text_input("Search by Event Title")
            event_types = df["EVENT_TYPE"].dropna().unique().tolist()
            selected_type = st.selectbox("Filter by Event Type", ["All"] + event_types)

            try:
                cursor.execute("SELECT id, association_name FROM xabuteo.public.associations ORDER BY association_name")
                assoc_list = cursor.fetchall()
                assoc_map = {name: id for id, name in assoc_list}
                assoc_names = ["All"] + list(assoc_map.keys())
                selected_assoc = st.selectbox("Filter by Association", assoc_names)
            except:
                selected_assoc = "All"

        # Apply filters
        if search_text:
            df = df[df["EVENT_TITLE"].str.contains(search_text, case=False, na=False)]
        if selected_type != "All":
            df = df[df["EVENT_TYPE"] == selected_type]
        if selected_assoc != "All":
            assoc_id = assoc_map[selected_assoc]
            df = df[df["ASSOCIATION_ID"] == assoc_id]

        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading events: {e}")

    # --- Add New Event ---
    with st.expander("➕ Add New Event"):
        with st.form("event_form"):
            event_title = st.text_input("Event Title")
            event_type = st.selectbox("Event Type", ["Tournament", "Training", "Meeting", "Other"])
            event_open = st.checkbox("Open Event")
            event_women = st.checkbox("Women Only")
            event_junior = st.checkbox("Junior Event")
            event_veteran = st.checkbox("Veteran Event")
            event_teams = st.checkbox("Team Event")
            event_location = st.text_input("Event Location")

            event_start_date = st.date_input("Start Date")
            event_end_date = st.date_input("End Date")
            reg_open_date = st.date_input("Registration Opens")
            reg_close_date = st.date_input("Registration Closes")

            event_status = st.selectbox("Status", ["Pending", "Confirmed", "Cancelled"])
            event_email = st.text_input("Contact Email")
            event_comments = st.text_area("Comments")

            # Association dropdown again
            try:
                cursor.execute("SELECT id, association_name FROM xabuteo.public.associations ORDER BY association_name")
                associations = cursor.fetchall()
                assoc_map_insert = {name: id for id, name in associations}
                association_name = st.selectbox("Association", list(assoc_map_insert.keys()))
                association_id = assoc_map_insert[association_name]
            except:
                st.warning("Failed to load associations.")
                association_id = None

            submitted = st.form_submit_button("Submit")
            if submitted:
                if not event_title or not association_id:
                    st.warning("Event title and association are required.")
                else:
                    try:
                        cursor.execute("""
                            INSERT INTO xabuteo.public.events (
                                Event_Title, Association_ID, Event_Type,
                                Event_Open, Event_Women, Event_Junior, Event_Veteran, Event_Teams,
                                Event_Location, Event_Start_Date, Event_End_Date,
                                Reg_Open_Date, Reg_Close_Date, Event_Status,
                                Event_Email, Event_Comments
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            event_title, association_id, event_type,
                            event_open, event_women, event_junior, event_veteran, event_teams,
                            event_location, event_start_date, event_end_date,
                            reg_open_date, reg_close_date, event_status,
                            event_email, event_comments
                        ))
                        conn.commit()
                        st.success("✅ Event added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error inserting event: {e}")

    cursor.close()
    conn.close()
