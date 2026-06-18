import streamlit as st
import pandas as pd
import json
import os
import requests

st.set_page_config(layout="wide", page_title="Badminton Pro Coach")

# --- 1. DATA LOADING FUNCTION ---
def load_data():
    if os.path.exists("unified.json") and os.path.exists("heatmaps.json"):
        df = pd.read_json("unified.json")
        with open("heatmaps.json", "r") as f:
            hm = json.load(f)
        return df, hm
    return pd.DataFrame(), None

# --- 2. SIDEBAR ---
st.sidebar.header("📹 Input & Settings")
uploaded_file = st.sidebar.file_uploader("Upload Badminton Video", type=["mp4", "mov", "avi"])

# --- 3. LOGIC: ONLY LOAD DATA IF FILE UPLOADED ---
if uploaded_file:
    st.sidebar.success(f"Video Loaded: {uploaded_file.name}")
    st.sidebar.video(uploaded_file)
    
    df, hm = load_data()
    
    if not df.empty and hm:
        st.title("🏸 Badminton Performance Pro")
        
        # Dashboard Content
        selected_movement = st.sidebar.selectbox("Choose Footwork Pattern:", df['footwork_label'].unique())
        f_df = df[df['footwork_label'] == selected_movement]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Frames", hm['metadata']['total_frames_compiled'])
        col2.metric("Avg Speed", f"{f_df['speed_smoothed'].mean():.2f}")
        col3.metric("Max Speed", f"{f_df['speed_smoothed'].max():.2f}")
        col4.metric("Efficiency", f"{f_df['path_efficiency'].mean():.2%}")

        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.subheader(f"Movement: {selected_movement}")
            st.scatter_chart(f_df, x='hip_center_x', y='hip_center_y', color='speed', size='speed')
        with c2:
            st.subheader("Court Zone Distribution")
            occ = pd.DataFrame.from_dict(hm['court_occupancy_bin_percentages'], orient='index', columns=['%'])
            st.bar_chart(occ)

        # --- 4. AI TACTICAL COACH ---
       # --- 4. AI TACTICAL COACH ---
        with st.expander("🤖 Click for AI Tactical Advice", expanded=True):
            if st.button("Generate Tactical Analysis"):
                with st.spinner("Analyzing movement..."):
                    # FAIL-SAFE API KEY LOADING
                    try:
                        api_key = st.secrets["GROQ_API_KEY"]
                    except:
                        # FALLBACK: Used only if .streamlit/secrets.toml is missing
                        api_key = None
                    if not api_key:
                     st.error("API Key not found. Please set it in Streamlit Cloud Settings.")
                    
                    prompt = f"As a professional coach, analyze movement {selected_movement} with avg speed {f_df['speed_smoothed'].mean():.2f}. Provide 2 expert tactical tips."
                    
                    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
                    
                    try:
                        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                                headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=60)
                        if response.status_code == 200:
                            st.markdown(f"### 📋 Coach's Report\n{response.json()['choices'][0]['message']['content']}")
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")
    else:
        st.error("Data files (unified.json/heatmaps.json) not found in the project folder!")
else:
    # This is what they see BEFORE uploading
    st.title("🏸 Badminton Performance Pro")
    st.info("Please upload a video file in the sidebar to begin the analysis.")
    st.write("---")
    st.write("### Welcome to your Pro Coach Dashboard")
    st.write("This platform provides biomechanical analysis and tactical feedback for badminton athletes.")
