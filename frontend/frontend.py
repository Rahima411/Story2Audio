import streamlit as st
import requests
import base64

# Page configuration
st.set_page_config(page_title="TTS Demo", page_icon="🔊", layout="centered")

# Header
st.markdown("""
    <h1 style='text-align: center;'>TTS Microservice Demo</h1>
    <p style='text-align: center; color: gray;'>Convert your text into speech using our microservice architecture!</p>
    <hr>
""", unsafe_allow_html=True)

# Input Section
with st.container():
    st.subheader("Enter Text")
    text = st.text_area("Type your message below:", "Hello, this is a test.", height=150)

# Generate Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate = st.button("Generate Audio", use_container_width=True)

# Output Section
if generate:
    with st.spinner("Synthesizing speech..."):
        try:
            response = requests.post("http://tts-rest-client:8000/generate", json={"text": text})
            if response.status_code == 200:
                data = response.json()
                audio_bytes = base64.b64decode(data["audio_data"])

                st.markdown("### Output Audio")
                st.audio(audio_bytes, format="audio/wav")
                st.success(" Audio generated successfully!")
            else:
                st.error(" Failed to generate audio. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f" Error: Could not connect to the TTS service.\n\n{e}")
