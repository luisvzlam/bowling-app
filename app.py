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

# --- 📊 SECTION 4: TOP 5 LEADERBOARD ---
st.header("🏆 Top 5 Leaderboard")

try:
    # 1. We tell Supabase to get the score AND the name from the linked player table
    # 2. We order by score_value (High to Low)
    # 3. We limit to the top 5
    res = db.table("scores").select("""
        score_value,
        players ( name )
    """).order("score_value", desc=True).limit(5).execute()

    if res.data:
        # We clean the data so it looks nice in the table (removing brackets/braces)
        formatted_leaderboard = [
            {"Player": row['players']['name'], "Score": row['score_value']} 
            for row in res.data
        ]
        st.table(formatted_leaderboard)
    else:
        st.info("No scores found yet!")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")
    st.info("💡 Tip: Ensure your 'scores' table has a Foreign Key column linking to 'players'.")

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
