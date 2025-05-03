import streamlit as st
import requests
import base64
import json
import os
import io
# from streamlit_lottie import st_lottie

# Page configuration
st.set_page_config(page_title="📚 TTS Storybook", page_icon="📖", layout="centered")

# # --- Load Lottie Animation ---
# def load_lottie(path):
#     with open(path, "r") as f:
#         return json.load(f)

# # --- Lottie Animation for Title (Optional) ---
# if os.path.exists("assets/story_title.json"):
#     title_anim = load_lottie("assets/story_title.json")
#     st_lottie(title_anim, speed=1, loop=False, height=250)

# --- Custom CSS Styles ---
st.markdown("""
    <style>
        .stTextArea textarea {
            font-size: 16px;
            font-family: 'Comic Sans MS', cursive;
            border-radius: 10px;
            border: 1px solid #cccccc;
        }
        .stButton>button {
            background-color: #f7b731;
            color: white;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            height: 3em;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #e0a800;
        }
        .header-title {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            font-family: 'Comic Sans MS', cursive;
            margin-bottom: 0.2em;
        }
        .header-subtitle {
            text-align: center;
            color: gray;
            font-size: 1.3em;
            margin-bottom: 1em;
        }
        .centered-button {
            display: flex;
            justify-content: center;
            margin-top: 1.5em;
        }
        .download-button {
            background-color: #f7b731;
            color: white;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            padding: 15px 40px;
            transition: all 0.3s ease-in-out;
        }
        .download-button:hover {
            background-color: #e0a800;
            transform: scale(1.1); /* Slight zoom effect on hover */
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='header-title'>📖 TTS Storybook</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Bring stories to life through voices and imagination!</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Voice Selection & Theme Placeholder ---
voice = st.selectbox("🎤 Choose a Voice", ["Default", "Female", "Male", "Robot"])

# --- Input Section ---
st.subheader("📝 Enter Your Story Below")
text = st.text_area("Once upon a time...", "A little bunny went on an adventure...", height=150)
st.session_state["text"] = text

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
                # if os.path.exists("assets/flip.wav"):
                #     st.markdown("""
                #     <audio autoplay>
                #       <source src="assets/flip.wav" type="audio/wav">
                #     </audio>
                #     """, unsafe_allow_html=True)

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


# --- Fun Footer ---
st.markdown("""
<hr style="border: 1px solid #ccc;">
<div style="text-align: center; font-size: 1.2em; padding-top: 1em;">
  Made with ❤️ for little dreamers by <strong>Rahima</strong> and <strong>Mehru</strong> ✨
</div>
""", unsafe_allow_html=True)

