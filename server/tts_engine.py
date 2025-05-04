import os
import time
import io
import torch
import torchaudio

from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from text_preprocessing import preprocess_for_tts

class TextToSpeechEngine:
    def __init__(self, model_dir="./models"):
        self.device = torch.device("cpu")
        self.processor = None
        self.model = None
        self.vocoder = None
        self.voice_embeddings = {}

        self.model_dir = model_dir
        self.processor_dir = os.path.join(model_dir, "processor")
        self.tts_dir = os.path.join(model_dir, "speecht5_tts")
        self.vocoder_dir = os.path.join(model_dir, "speecht5_hifigan")
        self.emb_dir = os.path.join(model_dir, "spk_embs")

        self.voice_map = {
            "default": "female_0",
            "female 1": "female_0",
            "male 1": "male_0",
            "female 2": "female_1",
            "male 2": "male_1",  
        }

        self._load_models()
        self._load_embeddings()

    def _load_models(self):
        print("🧠 Loading TTS Models...")
        self.processor = SpeechT5Processor.from_pretrained(self.processor_dir, local_files_only=True)
        self.model = SpeechT5ForTextToSpeech.from_pretrained(self.tts_dir).to(self.device).eval()
        self.vocoder = SpeechT5HifiGan.from_pretrained(self.vocoder_dir).to(self.device).eval()

    def _load_embeddings(self):
        print("🎙️ Loading voice embeddings...")
        for fname in os.listdir(self.emb_dir):
            if fname.endswith(".pt"):
                voice_name = fname.replace(".pt", "")
                emb_path = os.path.join(self.emb_dir, fname)
                self.voice_embeddings[voice_name] = torch.load(emb_path).to(self.device)

        if "default" not in self.voice_embeddings:
            self.voice_embeddings["default"] = list(self.voice_embeddings.values())[0]

    def generate(self, text, voice="default"):
        chunks = preprocess_for_tts(text)
        if not chunks:
            raise ValueError("Text is empty after preprocessing.")

        voice_key = self.voice_map.get(voice.lower(), "default")
        speaker_embedding = self.voice_embeddings.get(voice_key, self.voice_embeddings["default"])

        audio_bytes = b""
        start_time = time.time()

        for chunk in chunks:
            inputs = self.processor(text=chunk, return_tensors="pt").to(self.device)

            with torch.no_grad():
                speech = self.model.generate(**inputs, speaker_embeddings=speaker_embedding)

            with torch.no_grad():
                waveform = self.vocoder(speech).cpu().squeeze(0)

            buffer = io.BytesIO()
            torchaudio.save(buffer, waveform.unsqueeze(0), sample_rate=16000, format="wav")
            audio_bytes += buffer.getvalue()

        elapsed = time.time() - start_time
        return audio_bytes, chunks, elapsed
