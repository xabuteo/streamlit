import streamlit as st
import pandas as pd
from utils import get_snowflake_connection

def show():
    st.title("🗂️ Club Requests")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT pc.id, r.first_name || ' ' || r.last_name AS player_name, 
                   c.club_name, pc.valid_from, pc.valid_to, pc.player_status
            FROM xabuteo.public.player_club pc
            JOIN xabuteo.public.registrations r ON pc.player_id = r.id
            JOIN xabuteo.public.clubs c ON pc.club_id = c.id
            WHERE pc.player_status = 'Pending'
            ORDER BY pc.valid_from DESC
        """)
        rows = cursor.fetchall()
        cols = [desc[0].lower() for desc in cursor.description]

        if not rows:
            st.info("✅ No pending club requests.")
            return

        df = pd.DataFrame(rows, columns=cols)

        # Show pending requests as a clean table
        st.dataframe(df.drop(columns=["id", "player_status"]), use_container_width=True, hide_index=True)

        # Add approve/reject buttons for each row
        st.markdown("### ✍️ Manage Requests")
        for i, row in df.iterrows():
            with st.container():
                st.write(f"**{row['player_name']}** → **{row['club_name']}** ({row['valid_from']} to {row['valid_to']})")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", key=f"approve_{row['id']}"):
                        cursor.execute("UPDATE xabuteo.public.player_club SET player_status = 'Approved' WHERE id = %s", (row['id'],))
                        conn.commit()
                        st.success(f"Approved {row['club_name']} for {row['player_name']}")
                        st.experimental_rerun()
                with col2:
                    if st.button("❌ Reject", key=f"reject_{row['id']}"):
                        cursor.execute("UPDATE xabuteo.public.player_club SET player_status = 'Rejected' WHERE id = %s", (row['id'],))
                        conn.commit()
                        st.warning(f"Rejected {row['club_name']} for {row['player_name']}")
                        st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Error loading requests: {e}")
    finally:
        cursor.close()
        conn.close()
