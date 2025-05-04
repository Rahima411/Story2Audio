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
pt_files = [f for f in os.listdir(embeddings_dir) if f.endswith(".pt")]
if pt_files:
    for fname in pt_files:
        key = os.path.splitext(fname)[0]  # e.g., male_0 from male_0.pt
        path = os.path.join(embeddings_dir, fname)
        embeddings[key] = torch.load(path).to(device)
    print(f"📦 Loaded {len(embeddings)} speaker embeddings.")
else:
    print("🌐 No local speaker embeddings found. Downloading default embeddings...")
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_map = {
        "male": [7306, 7310],
        "female": [7309, 7311]
    }
    for gender, indices in speaker_map.items():
        for i, idx in enumerate(indices):
            speaker_embedding = torch.tensor(embeddings_dataset[idx]["xvector"]).unsqueeze(0)
            save_name = f"{gender.lower()}_{i}.pt"
            save_path = os.path.join(embeddings_dir, save_name)
            torch.save(speaker_embedding, save_path)
            embeddings[f"{gender.lower()}_{i}"] = speaker_embedding.to(device)
            print(f"✅ Saved {gender.title()} embedding at: {save_path}")

            
# Input text
text = "Hello! This is a text-to-speech test using SpeechT5 running offline."

# Tokenize
inputs = processor(text=text, return_tensors="pt").to(device)

# Generate speech (spectrogram)
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
