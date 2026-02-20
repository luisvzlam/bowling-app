import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Tribu Strike", page_icon="🎳")

# 2. Secure Connection Setup
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    db = create_client(URL, KEY)
else:
    st.error("Missing Secrets! Go to Streamlit Settings and add SUPABASE_URL and SUPABASE_KEY.")
    st.stop()

# 3. App Title
st.title("🎳 Tribu Strike")

# --- 📊 SECTION 4: ALL-TIME TOP 5 SCORES ---
st.header("🏆 Top 5 Scores")

try:
    # Fetch scores, including the new 'game' and 'created_at' columns
    res = db.table("scores").select("""
        score_value,
        game,
        created_at,
        players ( name )
    """).order("score_value", desc=True).limit(5).execute()

    if res.data:
        leaderboard = [
            {
                "Player": row['players']['name'], 
                "Score": row['score_value'],
                "Game #": row.get('game', 'N/A'),
                "Date": row.get('created_at', '')[:10] # Formats timestamp to YYYY-MM-DD
            } 
            for row in res.data
        ]
        
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)
    else:
        st.info("No scores recorded yet!")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")

# --- 📝 SECTION 5: RECORD A NEW SCORE ---
st.divider()
st.subheader("Add New Score")

# 1. Logic for "Last Monday" as default date
today = datetime.now()
days_to_subtract = today.weekday()  # Monday is 0
last_monday = today - timedelta(days=days_to_subtract)

try:
    # 2. Fetch current players
    player_res = db.table("players").select("id, name").execute()
    player_map = {p['name']: p['id'] for p in player_res.data} if player_res.data else {}
    
    player_options = ["+ Add New Player"] + list(player_map.keys())

    # 3. Selection outside the form
    selected_option = st.selectbox("Who is playing?", options=player_options)
    
    new_player_name = ""
    
    # 4. Form starts here
    with st.form("score_entry_form", clear_on_submit=True):
        
        if selected_option == "+ Add New Player":
            new_player_name = st.text_input("Enter New Player Name")
        else:
            st.info(f"Recording score for: **{selected_option}**")

        # Create two columns for Game # and Date
        col1, col2 = st.columns(2)
        with col1:
            game_num = st.number_input("Game #", min_value=1, step=1, value=1)
        with col2:
            play_date = st.date_input("Date of Game", value=last_monday)

        new_score = st.number_input("Score", min_value=0, max_value=300, step=1)
        submit_score = st.form_submit_button("Save Score")

        if submit_score:
            target_id = None
            
            # Step A: Handle New Player
            if selected_option == "+ Add New Player":
                if new_player_name.strip():
                    new_p_res = db.table("players").insert({"name": new_player_name.strip()}).execute()
                    target_id = new_p_res.data[0]['id']
                else:
                    st.error("Please provide a name!")
                    st.stop()
            else:
                target_id = player_map[selected_option]

            # Step B: Insert Score with new columns
            if target_id:
                db.table("scores").insert({
                    "player_id": target_id, 
                    "score_value": new_score,
                    "game": game_num,         # Matches your new DB column
                    "created_at": str(play_date) # Matches your DB date column
                }).execute()
                
                st.success("Score saved!")
                st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
