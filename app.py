import streamlit as st
import pandas as pd
import json
import glob

st.title("🏸 Badminton Coach Report")

# Automatically find the file starting with 'unified'
files = glob.glob("unified*.json")

if not files:
    st.error("No file starting with 'unified' found in this folder!")
    st.write("Current files found:", glob.glob("*"))
else:
    filename = files[0] # Pick the first file found
    st.write(f"Loading: {filename}")
    
    with open(filename, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    
    st.success("Data loaded successfully!")
    st.dataframe(df.head())
    st.line_chart(df['speed_smoothed'])
# Add this after st.subheader("Data Overview")
footwork_type = st.selectbox("Select Footwork Type", df['footwork_label'].unique())
filtered_df = df[df['footwork_label'] == footwork_type]
st.dataframe(filtered_df.head())
# Add this to show an instant stat
st.metric("Avg Speed for selected movement", round(filtered_df['speed_smoothed'].mean(), 2))
# Add this snippet after your df = pd.DataFrame(data) line
movement_options = df['footwork_label'].unique()
selected_movement = st.sidebar.selectbox("Choose a movement to analyze:", movement_options)

# Filter the data
filtered_df = df[df['footwork_label'] == selected_movement]

st.subheader(f"Analysis for: {selected_movement}")
st.line_chart(filtered_df['speed_smoothed'])
# Add this right under your subheader
col1, col2, col3 = st.columns(3)
col1.metric("Avg Speed", f"{round(filtered_df['speed_smoothed'].mean(), 2)}")
col2.metric("Max Speed", f"{round(filtered_df['speed_smoothed'].max(), 2)}")
col3.metric("Avg Recovery", f"{round(filtered_df['recovery_time'].mean(), 2)} frames")
st.subheader("Movement Hotspots")
# Using hip_center_x and hip_center_y as the tracking coordinates
st.scatter_chart(filtered_df, x='hip_center_x', y='hip_center_y')
st.subheader("Movement Intensity Map")

# We color-code by 'speed' to show intensity
# We use hip_center coordinates to map the court position
st.scatter_chart(
    filtered_df, 
    x='hip_center_x', 
    y='hip_center_y', 
    color='speed', 
    size='speed'
)
st.caption("Dots scale by intensity: Larger/brighter dots = higher speed bursts.")
st.subheader("Efficiency Report")
# Group by footwork label to see which one has the lowest path efficiency
efficiency_df = filtered_df.groupby('footwork_label')['path_efficiency'].mean().reset_index()
st.bar_chart(efficiency_df.set_index('footwork_label'))
# Create a dashboard header layout
col1, col2 = st.columns([1, 1]) # Splits the page 50/50

with col1:
    st.subheader("Intensity Map")
    st.scatter_chart(filtered_df, x='hip_center_x', y='hip_center_y', color='speed')

with col2:
    st.subheader("Efficiency")
    st.bar_chart(filtered_df.groupby('footwork_label')['path_efficiency'].mean())
primaryColor = "#F63366"  # A sharp 'Badminton Red'
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"