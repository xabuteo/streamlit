import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("📅 Events")

    query_params = st.query_params
    selected_event_id = query_params.get("event_id", [None])[0]

    if selected_event_id:
        show_event_details(selected_event_id)
        return
    
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
        "ASSOCIATION_ID", "EVENT_COMMENTS", "REG_OPEN_DATE", "REG_CLOSE_DATE",
        "EVENT_EMAIL", "EVENT_OPEN", "EVENT_WOMEN", "EVENT_JUNIOR", "EVENT_VETERAN",
        "EVENT_TEAMS", "UPDATE_TIMESTAMP"
    }
    display_cols = [col for col in df.columns if col not in hide_cols]
    df_display = df[display_cols]

    st.subheader("📋 Event List")
    
    def make_event_link(row):
        return f"[{row['EVENT_TITLE']}](/?event_id={row['ID']})"
    
    df_display["Event Link"] = df_display.apply(make_event_link, axis=1)
    
    # Display events with clickable links using HTML table
    st.markdown("### 📋 Event List")
    
    # Create HTML table
    table_html = """
    <table style="width:100%">
        <thead>
            <tr>
                <th align="left">Event Title</th>
                <th align="left">Type</th>
                <th align="left">Start Date</th>
                <th align="left">End Date</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in df_display.iterrows():
        table_html += f"""
            <tr>
                <td><a href="/?event_id={row['ID']}" target="_self">{row['EVENT_TITLE']}</a></td>
                <td>{row['EVENT_TYPE']}</td>
                <td>{row['EVENT_START_DATE']}</td>
                <td>{row['EVENT_END_DATE']}</td>
            </tr>
        """
    
    table_html += "</tbody></table>"
    
    # Render HTML safely
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Add new event
    with st.expander("➕ Add New Event"):
        with st.form("add_event_form"):
            col1, col2 = st.columns(2)
            with col1:            
                title = st.text_input("Event Title")
            with col2:            
                # Fetch event types from lookup table
                try:
                    conn = get_snowflake_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT list_value
                        FROM xabuteo.public.ref_lookup
                        WHERE list_type = 'event_type'
                        ORDER BY list_order
                    """)
                    event_types = [row[0] for row in cursor.fetchall()]
                except Exception as e:
                    st.error(f"Error loading event types: {e}")
                    event_types = []
                finally:
                    cursor.close()
                    conn.close()
        
                event_type = st.selectbox("Event Type", event_types)

            col1, col2 = st.columns(2)
            with col1:            
                start_date = st.date_input("Start Date")
            with col2:            
                end_date = st.date_input("End Date")

            col1, col2 = st.columns(2)
            with col1:            
                reg_open_date = st.date_input("Registration Open Date")
            with col2:            
                reg_close_date = st.date_input("Registration Close Date")
            
            location = st.text_input("Location")
    
            # Checkboxes
            col1, col2, col3 = st.columns(3)
            with col1:
                event_open = st.checkbox("Open")
                event_women = st.checkbox("Women")
            with col2:
                event_junior = st.checkbox("Junior")
                event_veteran = st.checkbox("Veteran")
            with col3:
                event_teams = st.checkbox("Teams")

            event_email = st.text_input("Contact Email")
    
            comments = st.text_area("Comments")
    
            submit = st.form_submit_button("Add Event")
    
            if submit:
                try:
                    conn = get_snowflake_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO xabuteo.public.events (
                            event_title, event_type, event_location,
                            event_start_date, event_end_date,
                            reg_open_date, reg_close_date,
                            event_email, event_open, event_women,
                            event_junior, event_veteran, event_teams,
                            event_comments
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        title, event_type, location,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        reg_open_date.strftime('%Y-%m-%d'),
                        reg_close_date.strftime('%Y-%m-%d'),
                        event_email, event_open, event_women,
                        event_junior, event_veteran, event_teams,
                        comments
                    ))
                    conn.commit()
                    st.success("✅ Event added successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error inserting event: {e}")
                finally:
                    cursor.close()
                    conn.close()

def show_event_details(event_id):
    st.markdown("🔙 [Back to Events](?event_id=)")

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM xabuteo.public.events_v WHERE id = %s", (event_id,))
        row = cursor.fetchone()
        cols = [desc[0] for desc in cursor.description]
        event = dict(zip(cols, row)) if row else None
    except Exception as e:
        st.error(f"Error loading event details: {e}")
        return
    finally:
        cursor.close()
        conn.close()

    if not event:
        st.warning("Event not found.")
        return

    st.header(event.get("EVENT_TITLE", "Event Details"))
    st.write("### Details")
    for key, value in event.items():
        st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    if st.button("📝 Register for this Event"):
        st.success("Registration functionality coming soon!")  # Replace with actual registration logic
