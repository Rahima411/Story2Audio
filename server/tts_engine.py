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
            "Default": "slt",  # US Female (default fallback)
            "US Female 1": "slt",
            "US Female 2": "clb",
            "US Male 1": "bdl",
            "US Male 2": "rms",
            "Canadian Male": "jmk",
            "Scottish Male": "awb",
            "Indian Male": "ksp",
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
        if not os.path.exists(self.emb_dir):
            raise FileNotFoundError(f"Embedding directory {self.emb_dir} does not exist")
            
        for fname in os.listdir(self.emb_dir):
            if fname.endswith(".pt"):
                voice_name = fname.replace(".pt", "")
                emb_path = os.path.join(self.emb_dir, fname)
                try:
                    # Load the embedding
                    embedding = torch.load(emb_path).to(self.device)
                    
                    # Ensure it has the correct shape with batch dimension
                    if embedding.dim() == 1:  # If it's just [512]
                        embedding = embedding.unsqueeze(0)  # Make it [1, 512]
                    
                    # Store the correctly shaped embedding
                    self.voice_embeddings[voice_name] = embedding
                    print(f"Speaker {voice_name}: tensor shape {embedding.shape}, dtype {embedding.dtype}")
                except Exception as e:
                    print(f"Failed to load embedding {emb_path}: {str(e)}")
                    
        if not self.voice_embeddings:
            raise ValueError(f"No voice embeddings found in {self.emb_dir}")
            
        if "default" not in self.voice_embeddings:
            self.voice_embeddings["default"] = list(self.voice_embeddings.values())[0]
            
    def generate(self, text, voice="default"):
        try:
            chunks = preprocess_for_tts(text)
            if not chunks:
                raise ValueError("Text is empty after preprocessing.")
                
            voice_id = self.voice_map.get(voice, "slt")
            if voice_id not in self.voice_embeddings:
                print(f"Voice ID {voice_id} not found, falling back to default")
                voice_id = "slt" if "slt" in self.voice_embeddings else list(self.voice_embeddings.keys())[0]
                
            voice_embedding = self.voice_embeddings[voice_id]
            print(f"Using voice {voice_id} with embedding shape: {voice_embedding.shape}")
            
            audio_bytes = b""
            start_time = time.time()
            
            for chunk in chunks:
                inputs = self.processor(text=chunk, return_tensors="pt").to(self.device)
                
                # Check batch size of inputs to ensure compatibility
                batch_size = inputs.input_ids.shape[0]
                if voice_embedding.shape[0] != 1 and voice_embedding.shape[0] != batch_size:
                    # Ensure speaker_embeddings has the correct batch dimension
                    voice_embedding = voice_embedding.expand(batch_size, -1)
                    print(f"Adjusted embedding shape to: {voice_embedding.shape}")
                
                with torch.no_grad():
                    speech = self.model.generate(**inputs, speaker_embeddings=voice_embedding)
                    
                with torch.no_grad():
                    waveform = self.vocoder(speech).cpu().squeeze(0)
                    buffer = io.BytesIO()
                    torchaudio.save(buffer, waveform.unsqueeze(0), sample_rate=16000, format="wav")
                    audio_bytes += buffer.getvalue()
                    
            elapsed = time.time() - start_time
            return audio_bytes, chunks, elapsed
            
        except Exception as e:
            print(f"Error during TTS generation: {str(e)}")
            import traceback
            traceback.print_exc()
            raise