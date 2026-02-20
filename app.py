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

# --- 📊 SECTION 4: HIGHEST SCORE LEADERBOARD ---
st.header("🏆 Top 5 High Scores")

try:
    # 1. Fetch scores and player names
    res = db.table("scores").select("""
        score_value,
        players ( name )
    """).execute()

    if res.data:
        # 2. Logic to keep only the HIGHEST score for each player
        highest_scores = {}
        for row in res.data:
            name = row['players']['name']
            score = row['score_value']
            
            # If player not seen or this score is higher than their previous record
            if name not in highest_scores or score > highest_scores[name]:
                highest_scores[name] = score

        # 3. Format, Sort, and Limit to Top 5
        leaderboard = [
            {"Player": name, "High Score": score} 
            for name, score in highest_scores.items()
        ]
        # Sort by score descending
        leaderboard = sorted(leaderboard, key=lambda x: x['High Score'], reverse=True)[:5]
        
        st.table(leaderboard)
    else:
        st.info("No scores recorded yet!")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")
# This tells Streamlit to display the data without the row numbers
st.dataframe(leaderboard, hide_index=True, use_container_width=True)

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
