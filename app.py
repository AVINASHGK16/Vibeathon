import streamlit as st
import sqlite3
import string
import random
import pandas as pd

# --- DB Setup (Data Persistence) ---
conn = sqlite3.connect('links.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS links
             (short_id TEXT PRIMARY KEY, original_url TEXT, clicks INTEGER)''')
conn.commit()

def generate_short_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# --- Routing & Redirection ---
# Check if the user is accessing a short link via query parameter (e.g., ?id=xyz)
params = st.query_params
if "id" in params:
    short_id = params["id"]
    c.execute("SELECT original_url, clicks FROM links WHERE short_id=?", (short_id,))
    result = c.fetchone()
    
    if result:
        original_url, clicks = result
        # Increment click count
        c.execute("UPDATE links SET clicks = clicks + 1 WHERE short_id=?", (short_id,))
        conn.commit()
        # Redirect using HTML meta refresh
        st.markdown(f'<meta http-equiv="refresh" content="0;url={original_url}">', unsafe_allow_html=True)
        st.stop() # Stop rendering the dashboard

# --- Main UI (Dashboard) ---
st.title("🚀 Link Analytics Shortener")

# 1. URL Shortening & Validation
st.subheader("Create a Short Link")
url_input = st.text_input("Enter Long URL (must include http:// or https://):")

if st.button("Shorten URL"):
    if url_input and (url_input.startswith("http://") or url_input.startswith("https://")):
        short_id = generate_short_id()
        c.execute("INSERT INTO links (short_id, original_url, clicks) VALUES (?, ?, ?)", (short_id, url_input, 0))
        conn.commit()
        
        # Construct the short link dynamically based on where the app is hosted
        # Using Streamlit's experimental_get_query_params is deprecated, we build a relative link
        st.success("Link Shortened Successfully!")
        st.code(f"?id={short_id}", language="text")
        st.info(f"Test it by adding `?id={short_id}` to your current URL!")
    else:
        st.error("Invalid input. Please enter a valid URL starting with http:// or https://")

# 2. Link Dashboard
st.subheader("📊 Analytics Dashboard")
df = pd.read_sql_query("SELECT original_url as 'Original URL', short_id as 'Short ID', clicks as 'Total Clicks' FROM links", conn)

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("No links created yet.")