import streamlit as st
import pandas as pd
import json
import requests
import glob

st.set_page_config(layout="wide", page_title="Badminton Pro Coach")

# --- 1. DATA LOADING ---
@st.cache_data
def load_data():
    u_files = glob.glob("unified*.json")
    df = pd.read_json(u_files[0]) if u_files else pd.DataFrame()
    with open("heatmaps.json", "r") as f:
        hm = json.load(f)
    return df, hm

df, hm = load_data()

# --- 2. SIDEBAR: VIDEO & SELECTION ---
st.sidebar.header("📹 Input & Settings")
uploaded_file = st.sidebar.file_uploader("Upload Badminton Video", type=["mp4", "mov", "avi"])

if uploaded_file:
    st.sidebar.success("Video Processed Successfully!")
    st.sidebar.video(uploaded_file)

st.sidebar.divider()
selected_movement = st.sidebar.selectbox("Choose Footwork Pattern:", df['footwork_label'].unique())
f_df = df[df['footwork_label'] == selected_movement]

# --- 3. MAIN DASHBOARD ---
st.title("🏸 Badminton Performance Pro")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Frames", hm['metadata']['total_frames_compiled'])
col2.metric("Avg Speed", f"{f_df['speed_smoothed'].mean():.2f}")
col3.metric("Max Speed", f"{f_df['speed_smoothed'].max():.2f}")
col4.metric("Efficiency", f"{f_df['path_efficiency'].mean():.2%}")

c1, c2 = st.columns([1.5, 1])
with c1:
    st.subheader(f"Movement Intensity: {selected_movement}")
    st.scatter_chart(f_df, x='hip_center_x', y='hip_center_y', color='speed', size='speed')

with c2:
    st.subheader("Court Zone Distribution")
    occ = pd.DataFrame.from_dict(hm['court_occupancy_bin_percentages'], orient='index', columns=['%'])
    st.bar_chart(occ)

# --- 4. AI TACTICAL COACH ---
with st.expander("🤖 Click for AI Tactical Advice", expanded=True):
    if st.button("Generate Tactical Analysis"):
        with st.spinner("Analyzing your movement..."):
            summary = f"Movement: {selected_movement}, Avg Speed: {f_df['speed_smoothed'].mean():.2f}."
            prompt = f"As a professional badminton coach, analyze: {summary}. Provide 2 expert tactical tips."
            
            # --- TESTING BLOCK ---
            api_key = st.secrets.get("GROQ_API_KEY") # PASTE YOUR KEY INSIDE THESE QUOTES
            
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "llama-3.3-70b-versatile",  # UPDATED MODEL NAME
                "messages": [{"role": "user", "content": prompt}]
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    report = response.json()['choices'][0]['message']['content']
                    st.markdown(f"### 📋 Coach's Report\n{report}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

st.caption("Pro-Tip: Compare different footwork types using the sidebar.")
