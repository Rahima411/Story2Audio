import os
import torch
import torchaudio
from transformers import (
    SpeechT5Processor,
    SpeechT5ForTextToSpeech,
    SpeechT5HifiGan,
)
from datasets import load_dataset

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"💻 Using device: {device}")

# Define model paths
model_dir = "./models"
processor_path = os.path.join(model_dir, "processor")
tts_model_path = os.path.join(model_dir, "speecht5_tts")
vocoder_path = os.path.join(model_dir, "speecht5_hifigan")
embeddings_path = os.path.join(model_dir, 'spk_embs')

saved_speakers = {}
embeddings = {}
speakers = ["bdl", "slt", "jmk", "awb", "rms", "clb", "ksp"]

# Create models directory if needed
os.makedirs(model_dir, exist_ok=True)

# Load or download processor
if os.path.exists(processor_path):
    processor = SpeechT5Processor.from_pretrained(processor_path)
    print("📦 Loaded processor from local storage.")
else:
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    processor.save_pretrained(processor_path)
    print("🌐 Downloaded and saved processor locally.")

# Load or download model
if os.path.exists(tts_model_path):
    model = SpeechT5ForTextToSpeech.from_pretrained(tts_model_path).to(device)
    print("📦 Loaded TTS model from local storage.")
else:
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)
    model.save_pretrained(tts_model_path)
    print("🌐 Downloaded and saved TTS model locally.")

# Load or download vocoder
if os.path.exists(vocoder_path):
    vocoder = SpeechT5HifiGan.from_pretrained(vocoder_path).to(device)
    print("📦 Loaded vocoder from local storage.")
else:
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(device)
    vocoder.save_pretrained(vocoder_path)
    print("🌐 Downloaded and saved vocoder locally.")

# Load or download embeddings
pt_files = [f for f in os.listdir(embeddings_path) if f.endswith(".pt")]
if pt_files:
    for fname in pt_files:
        key = os.path.splitext(fname)[0]
        path = os.path.join(embeddings_path, fname)
        embeddings[key] = torch.load(path).to(device)
    print(f"📦 Loaded {len(embeddings)} speaker embeddings from local files.")

# If embeddings not found locally, download from HF
if len(embeddings) < len(speakers):
    print("🌐 Some or all speaker embeddings missing. Downloading required x-vectors...")
    dataset = load_dataset("Matthijs/cmu-arctic-xvectors")["validation"]

    for item in dataset:
        filename = item["filename"]
        if "cmu_us_" in filename:
            parts = filename.split("_")
            if len(parts) >= 3:
                speaker_id = parts[2]
                if speaker_id in speakers and speaker_id not in embeddings:
                    xvector = torch.tensor(item["xvector"], dtype=torch.float)
                    if xvector.dim() == 1:
                        xvector = xvector.unsqueeze(0)
                    elif xvector.shape[0] != 1:
                        xvector = xvector[0].unsqueeze(0)
                    torch.save(xvector, os.path.join(embeddings_path, f"{speaker_id}.pt"))
                    embeddings[speaker_id] = xvector.to(device)
                    print(f"💾 Saved embedding for speaker {speaker_id} — shape: {xvector.shape}")
        if len(embeddings) == len(speakers):
            break






# Input text
text = "Hello! This is a text-to-speech test using SpeechT5 running offline."

# Tokenize
inputs = processor(text=text, return_tensors="pt").to(device)

# Generate speech (spectrogram)
speaker_id = "slt"  # US Female 1
speaker_embedding = embeddings.get(speaker_id)

print("🧠 Generating audio...")
with torch.no_grad():
    spectrogram = model.generate_speech(inputs["input_ids"], speaker_embedding)

# Use vocoder to convert to waveform
waveform = vocoder(spectrogram)
waveform = waveform.squeeze(0).cpu()

# Save the waveform as a playable audio file
output_path = "output.wav"
torchaudio.save(output_path, waveform.detach().unsqueeze(0), 16000)
print(f"✅ Audio saved at {output_path}")