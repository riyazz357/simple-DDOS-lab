

import streamlit as st
import sqlite3
import pandas as pd
import time
import altair as alt

st.set_page_config(page_title="DDoS War Room", page_icon="💥", layout="wide")

st.title("💥 Live DDoS Attack Monitor")

# --- DATA LOADER ---
def load_data():
    try:
        conn = sqlite3.connect('simulation.db')
        # We perform the aggregation IN SQL for speed
        query = "SELECT status_code, COUNT(*) as count FROM attack_logs GROUP BY status_code"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# --- THE LIVE LOOP ---
# Create a placeholder that we will overwrite every second
placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        if df.empty:
            st.info("Waiting for attack to launch... (Run 'python flood_db.py')")
        else:
            # --- 1. CALCULATE METRICS ---
            total_requests = df['count'].sum()
            
            # Count specifics
            try:
                success_count = df[df['status_code'] == 200]['count'].values[0]
            except: success_count = 0
            
            try:
                blocked_count = df[df['status_code'] == 429]['count'].values[0]
            except: blocked_count = 0
            
            try:
                failed_count = df[df['status_code'] == 500]['count'].values[0]
            except: failed_count = 0

            # --- 2. DISPLAY METRICS ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔥 Total Traffic", f"{total_requests}")
            col2.metric("✅ Server Success (200 OK)", f"{success_count}")
            col3.metric("🛡️ Firewall Blocked (429)", f"{blocked_count}", delta_color="inverse")
            col4.metric("💀 Server Crashed (500)", f"{failed_count}", delta_color="inverse")

            st.markdown("---")

            # --- 3. VISUALIZATIONS ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("🛡️ Attack Mitigation Status")
                # Pie Chart Data
                pie_data = pd.DataFrame({
                    'Category': ['Success (Passed)', 'Blocked (Filtered)', 'Crashed (Failed)'],
                    'Count': [success_count, blocked_count, failed_count]
                })
                
                # Custom color map: Green for good, Yellow for block, Red for fail
                base = alt.Chart(pie_data).encode(theta=alt.Theta("Count", stack=True))
                pie = base.mark_arc(outerRadius=120).encode(
                    color=alt.Color("Category", scale=alt.Scale(
                        domain=['Success (Passed)', 'Blocked (Filtered)', 'Crashed (Failed)'],
                        range=['#28a745', '#ffc107', '#dc3545']  # Green, Yellow, Red
                    )),
                    tooltip=["Category", "Count"]
                )
                st.altair_chart(pie, use_container_width=True)

            with c2:
                st.subheader("📊 Live Traffic Distribution")
                st.bar_chart(df.set_index('status_code'))

    # Refresh rate
    time.sleep(1)