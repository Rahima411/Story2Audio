import streamlit as st
import requests
import base64

st.title("🗣️ TTS Microservice Demo")

text = st.text_area("Enter text to synthesize:", "Hello, this is a test.")

if st.button("Generate"):
    with st.spinner("Contacting TTS service..."):
        response = requests.post("http://localhost:8000/generate", json={"text": text})
        if response.status_code == 200:
            data = response.json()
            audio_bytes = bytes(data["audio_data"])
            b64 = base64.b64encode(audio_bytes).decode()

            st.audio(audio_bytes, format="audio/wav")
            st.success("TTS audio generated!")
        else:
            st.error("Failed to generate audio.")
