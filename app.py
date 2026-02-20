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

# --- 📊 SECTION 4: ALL-TIME TOP 5 SCORES ---
st.header("🏆 Top 5 Leaderboard")

try:
    # 1. Fetch scores and names, ordered by score immediately in the query
    res = db.table("scores").select("""
        score_value,
        players ( name )
    """).order("score_value", desc=True).limit(5).execute()

    if res.data:
        # 2. Flatten the data (No "highest_score" dictionary needed here)
        leaderboard = [
            {"Player": row['players']['name'], "Score": row['score_value']} 
            for row in res.data
        ]
        
        # 3. Display the top scores
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)
    else:
        st.info("No scores recorded yet!")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")

# --- 📝 SECTION 5: RECORD A NEW SCORE ---
st.divider()
st.subheader("Add New Score")

try:
    # 1. Fetch current players
    player_res = db.table("players").select("id, name").execute()
    player_map = {p['name']: p['id'] for p in player_res.data} if player_res.data else {}
    
    # 2. Add a special option to the list
    player_options = ["+ Add New Player"] + list(player_map.keys())

    with st.form("score_form", clear_on_submit=True):
        selected_option = st.selectbox("Who is playing?", options=player_options)
        
        # 3. Show a text input ONLY if "+ Add New Player" is selected
        new_player_name = ""
        if selected_option == "+ Add New Player":
            new_player_name = st.text_input("Enter New Player Name")
        
        new_score = st.number_input("Score", min_value=0, max_value=300, step=1)
        submit_score = st.form_submit_button("Save Score")

        if submit_score:
            target_id = None
            
            # 4. If it's a new player, insert them into the 'players' table first
            if selected_option == "+ Add New Player":
                if new_player_name.strip():
                    new_p_res = db.table("players").insert({"name": new_player_name}).execute()
                    target_id = new_p_res.data[0]['id']
                else:
                    st.error("Please enter a name for the new player.")
                    st.stop()
            else:
                target_id = player_map[selected_option]

            # 5. Insert the score using the ID (either existing or newly created)
            if target_id:
                db.table("scores").insert({
                    "player_id": target_id,
                    "score_value": new_score
                }).execute()
                
                st.success(f"Score saved for {new_player_name if new_player_name else selected_option}!")
                st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
