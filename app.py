import streamlit as st
from supabase import create_client

# 1. Page Configuration
st.set_page_config(page_title="Bowling App", page_icon="🎳")

# 2. Secure Connection Setup
# We use st.secrets so your actual keys are NOT hardcoded in the script.
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    db = create_client(URL, KEY)
else:
    st.error("Missing Secrets! Go to Streamlit Settings and add SUPABASE_URL and SUPABASE_KEY.")
    st.stop()

# 3. App Title
st.title("🎳 Bowling App: Live Feed")

# 4. Display Section (Read)
st.header("Current Players")
try:
    res = db.table("players").select("*").execute()
    if res.data:
        st.dataframe(res.data, use_container_width=True)
    else:
        st.info("No players found. Use the form below to add one!")
except Exception as e:
    st.error(f"Database Error: {e}")

# 5. Input Section (Create)
st.divider()
st.subheader("Add New Player")
with st.form("player_entry", clear_on_submit=True):
    name = st.text_input("Player Name")
    if st.form_submit_button("Add to Database"):
        if name:
            try:
                db.table("players").insert({"name": name}).execute()
                st.success(f"Added {name}!")
                st.rerun() # Refreshes the list immediately
            except Exception as e:
                st.error(f"Failed to add player: {e}")
        else:
            st.warning("Please enter a name.")
