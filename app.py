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
    # 1. Fetch scores and join with player names
    # This pulls the score and the name associated with the player_id
    res = db.table("scores").select("""
        score_value,
        players ( name )
    """).execute()

    if res.data:
        # 2. Logic to keep only the HIGHEST score for each unique player
        highest_scores = {}
        for row in res.data:
            name = row['players']['name']
            score = row['score_value']
            
            # Update if this is the first time seeing the player or if they got a new PB
            if name not in highest_scores or score > highest_scores[name]:
                highest_scores[name] = score

        # 3. Format into a list of dictionaries for Streamlit
        leaderboard = [
            {"Player": name, "High Score": score} 
            for name, score in highest_scores.items()
        ]
        
        # 4. Sort by score (descending) and take the top 5
        leaderboard = sorted(leaderboard, key=lambda x: x['High Score'], reverse=True)[:5]
        
        # 5. Display the table cleanly
        # hide_index=True removes the "0" column
        # use_container_width=True makes it look great on all screens
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)
        
    else:
        st.info("No scores recorded yet! Add a score in Supabase to see it here.")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")

# --- 📝 SECTION 5: RECORD A NEW SCORE ---
st.divider()
st.subheader("Add New Score")

try:
    # 1. Fetch current players so we can choose one from a list
    player_res = db.table("players").select("id, name").execute()
    
    if player_res.data:
        # Create a dictionary to map names to IDs: {"Luis": 1, "Friend": 2}
        player_map = {p['name']: p['id'] for p in player_res.data}
        player_names = list(player_map.keys())

        with st.form("score_form", clear_on_submit=True):
            # Input fields
            selected_name = st.selectbox("Select Player", options=player_names)
            new_score = st.number_input("Enter Score", min_value=0, max_value=300, step=1)
            
            submit_score = st.form_submit_button("Save Score")

            if submit_score:
                # Get the ID for the selected name
                chosen_id = player_map[selected_name]
                
                # Insert the score into the 'scores' table
                db.table("scores").insert({
                    "player_id": chosen_id,
                    "score_value": new_score
                }).execute()
                
                st.success(f"Successfully saved score of {new_score} for {selected_name}!")
                st.rerun()
    else:
        st.warning("No players found. Please add a player in the database first!")

except Exception as e:
    st.error(f"Error loading players or saving score: {e}")
