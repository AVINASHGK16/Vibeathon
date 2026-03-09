import streamlit as st
import sqlite3
import string
import random
import pandas as pd

# --- Page Config & Custom CSS ---
st.set_page_config(page_title="VibeLink | Analytics", page_icon="🔗", layout="wide")

st.markdown("""
    <style>
    /* Hide Streamlit default headers and footers for a clean app look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style the primary button */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4F46E5;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease 0s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- DB Setup (Data Persistence) ---
conn = sqlite3.connect('links.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS links
             (short_id TEXT PRIMARY KEY, original_url TEXT, clicks INTEGER)''')
conn.commit()

def generate_short_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# --- Routing & Redirection ---
params = st.query_params
if "id" in params:
    short_id = params["id"]
    c.execute("SELECT original_url FROM links WHERE short_id=?", (short_id,))
    result = c.fetchone()
    
    if result:
        # Increment click count
        c.execute("UPDATE links SET clicks = clicks + 1 WHERE short_id=?", (short_id,))
        conn.commit()
        # Redirect seamlessly
        st.markdown(f'<meta http-equiv="refresh" content="0;url={result[0]}">', unsafe_allow_html=True)
        st.stop()

# --- Header ---
st.title("🔗 VibeLink Analytics")
st.markdown("Transform your long URLs into trackable, bite-sized links instantly.")
st.divider()

# --- Main Layout ---
# Split the screen into two columns for a dashboard feel
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.subheader("✨ Create a Short Link")
    url_input = st.text_input("Paste your long URL here:", placeholder="https://example.com/very/long/path")
    
    if st.button("Shorten URL 🚀"):
        if url_input and (url_input.startswith("http://") or url_input.startswith("https://")):
            short_id = generate_short_id()
            c.execute("INSERT INTO links (short_id, original_url, clicks) VALUES (?, ?, ?)", (short_id, url_input, 0))
            conn.commit()
            
            st.success("Link Shortened Successfully!")
            st.info(f"**Your tracking ID:** `?id={short_id}`")
            st.caption("Test it by adding this ID to your current web address.")
        else:
            st.error("⚠️ Invalid input. Please enter a valid URL starting with http:// or https://")

with col2:
    st.subheader("📈 Quick Stats")
    # Fetch high-level stats for the dashboard
    c.execute("SELECT COUNT(*), SUM(clicks) FROM links")
    stats = c.fetchone()
    total_links = stats[0] if stats[0] else 0
    total_clicks = stats[1] if stats[1] else 0
    
    # Display aesthetic metric widgets
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Total Links Created", value=total_links)
    metric_col2.metric(label="Total Clicks Tracked", value=total_clicks)

st.divider()

# --- Analytics Dashboard ---
st.subheader("📋 Link History")
# Retrieve data, ordering by the most clicked links first
df = pd.read_sql_query("SELECT short_id as 'Short ID', original_url as 'Original URL', clicks as 'Total Clicks' FROM links ORDER BY clicks DESC", conn)

if not df.empty:
    # Use container width and hide the ugly index column
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No links have been created yet. Be the first!")