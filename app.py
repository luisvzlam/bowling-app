import streamlit as st
from supabase import create_client

# -----------------------------
# 🔑 Supabase Connection
# -----------------------------
SUPABASE_URL = "https://lgiaftbwvsphqvxlhxij.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxnaWFmdGJ3dnNwaHF2eGxoeGlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE1MjU2MTUsImV4cCI6MjA4NzEwMTYxNX0.EqNQ7_LwS5I_vWfqCbumq0Z7OzmNJVu__R_vBf82K5o"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Bowling App", page_icon="🎳")

st.title("🎳 Bowling Score App")

# -----------------------------
# ➕ Create Player
# -----------------------------
st.header("Add New Player")

player_name = st.text_input("Player Name")

if st.button("Create Player"):
    if player_name:
        supabase.table("players").insert({"name": player_name}).execute()
        st.success("Player created successfully!")
    else:
        st.warning("Please enter a name.")

# -----------------------------
# 📋 Show Players
# -----------------------------
st.header("Players List")

response = supabase.table("players").select("*").execute()

if response.data:
    for player in response.data:
        st.write(f"ID: {player['id']} | Name: {player['name']}")
else:
    st.info("No players found.")
