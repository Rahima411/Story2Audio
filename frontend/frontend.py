import streamlit as st
import requests
import base64
import json
import os
import io

# Page configuration
st.set_page_config(page_title="📚 TTS Storybook", page_icon="📖", layout="centered")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Henny+Penny&family=Mystery+Quest&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- Custom CSS Styles ---
st.markdown("""
    <style>
        .stTextArea textarea {
            font-size: 16px;
            font-family: 'Comic Sans MS', cursive;
            border-radius: 10px;
            border: 1px solid #cccccc;
        }
        .stButton > button, .stDownloadButton > button {
            transition: all 0.3s ease-in-out;
            background-color: #6495ED !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            padding: 0.75rem 2rem !important;
            font-size: 16px !important;
            width: 100% !important;
            max-width: 300px !important;
            display: block;
            margin: auto;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(100, 149, 237, 0.7);
            background-color: #4169E1 !important;
        }

        .header-title {
            text-align: center;
            font-size: 5em;
            font-family: "Henny Penny", system-ui;
            font-weight: bold;
            margin-bottom: 0.2em;
        }
        .header-subtitle {
            text-align: center;
            font-family: "Mystery Quest", system-ui;
            color: gray;
            font-size: 1.3em;
            margin-bottom: 1em;
        }
    </style>
""", unsafe_allow_html=True)


# --- Header ---
st.markdown("<div class='header-title'>📖 TTS Storybook</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Bring stories to life through voices and imagination!</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Voice Selection & Theme Placeholder ---
mood = st.selectbox("🎭 Choose Your Mood", ["Happy", "Sad", "Scary"])
voice = st.selectbox(
    "🎤 Choose a Voice",
    ["Default", "US Female 1", "US Female 2", "US Male 1", "US Male 2", "Canadian Male", "Scottish Male", "Indian Male"]
)

if mood == "Happy":
    primary_color = "#f7b731"
    bg_color = "#fff8e1"
    secondary_bg = "#ffeaa7"
    text_color = "#2d3436"
elif mood == "Sad":
    bg_color = "#cfd8dc"
    secondary_bg = "#b0bec5"
    text_color = "#263238"
    primary_color = "#607d8b"
elif mood == "Scary":
    bg_color = "#212121"
    secondary_bg = "#424242"
    text_color = "#eeeeee"
    primary_color = "#d32f2f"

st.markdown(f"""
    <style>
        /* Override overall background */
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}

        /* Streamlit select boxes */
        section[data-testid="stSelectbox"] > div {{
            background-color: {secondary_bg} !important;
            color: {text_color} !important;
            border-radius: 10px !important;
        }}

        div[data-baseweb="select"] > div {{
            background-color: {secondary_bg} !important;
            color: {text_color} !important;
        }}

        /* Text area */
        .stTextArea textarea {{
            background-color: {secondary_bg} !important;
            color: {text_color} !important;
            border-radius: 10px !important;
            font-size: 16px !important;
        }}

        /* Buttons */
        .stButton > button, .stDownloadButton > button {{
            background-color: {primary_color} !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 10px !important;
        }}

        .stButton > button:hover {{
            background-color: #666 !important;
        }}

        /* Header (top navbar) */
        header {{
            background-color: {bg_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- Input Section ---
st.subheader("📝 Enter Your Story Below")
text = st.text_area("Once upon a time...", height=150)
st.session_state["text"] = text
st.session_state['voice'] = voice

# --- Generate Button ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate = st.button("🎧 Generate Audio")

# --- Output Section ---
if generate:
    with st.spinner("🔄 Turning your story into sound magic..."):
        try:
            response = requests.post("http://tts-rest-client:8000/generate", json={"text": text, "voice": voice})
            if response.status_code == 200:
                data = response.json()
                audio_bytes = base64.b64decode(data["audio_data"])
                time_taken = response.headers.get("X-Time-Taken") or data.get("time_taken")
                st.markdown("🧮 Character count: `{}`".format(len(st.session_state.get("text", ""))))
                chunks = data.get("chunks", [])

                with st.expander("🔍 Show Preprocessed Chunks (for curious minds)"):
                    for i, chunk in enumerate(chunks):
                        st.write(f"{chunk}")

                st.success("✅ Your magical audio story is ready!")
                st.audio(audio_bytes, format="audio/wav")

                # # Page flip sound
                # flip_sound_path = "flip.wav"
                # if os.path.exists(flip_sound_path):
                #     with open(flip_sound_path, "rb") as f:
                #         b64_audio = base64.b64encode(f.read()).decode()

                #     # Inject base64 audio tag with autoplay
                #     st.markdown(f"""
                #         <audio autoplay loop>
                #             <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                #         </audio>
                #     """, unsafe_allow_html=True)
                # else:
                #     st.warning("🔊 Page-flip audio file not found")

                # Centered download button
                with st.container():
                    st.markdown("<div class='centered-button-container'>", unsafe_allow_html=True)
                    st.download_button(
                        label="⬇️ Download Your Audio Story",
                        data=io.BytesIO(audio_bytes),
                        file_name="storybook.wav",
                        mime="audio/wav",
                        key="download_button",
                        use_container_width=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                if time_taken:
                    st.markdown(f"⏱️ Time taken: `{float(time_taken):.2f}` seconds")

            else:
                st.error("❌ Something went wrong while generating the story audio.")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Could not connect to the TTS microservice.\n\n{e}")


st.markdown("""
<hr style="border: 1px solid #ccc;">
<div style="text-align: center; font-size: 1.2em; padding-top: 1em;">
  Made with ❤️ for little dreamers by <strong>Rahima</strong> and <strong>Mehru</strong> ✨
</div>
""", unsafe_allow_html=True)

