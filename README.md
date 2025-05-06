# Story2Audio System

![Build](https://img.shields.io/github/actions/workflow/status/Rahima411/Story2Audio/ci.yml?branch=main)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/github/license/Rahima411/Story2Audio)

This project is a **Text-to-Speech (TTS)** system with a modular architecture, including a **Streamlit frontend**, **FastAPI backend**, and **gRPC** services for efficient communication. It converts text input into speech using pre-trained TTS models.

---

## 📚 Table of Contents
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Running the TTS Test Script](#running-the-tts-test-script)
- [Running the Full System](#running-the-full-system)
- [Configuration](#configuration)
- [Testing](#testing)
- [Usage](#usage)
- [Model Sources](#model-sources)
- [Limitations](#limitations)
- [Development Notes](#development-notes)
- [Contributing](#contributing)
- [License](#license)

---

## 📏 Architecture
```
├── client/                  # gRPC client implementation
│   ├── rest_gateway.py      # Core client functionality
│   └── Dockerfile          
├── common/                 # Shared protobuf/gRPC files
├── frontend/               # Streamlit web interface
│   ├── frontend.py         # Main frontend script
│   └── Dockerfile         
├── server/                 # TTS server implementation
│   ├── text_preprocessing.py   # Text normalization
│   ├── tts_engine.py       # Core TTS functionality
│   ├── server.py           # Core server functionality
│   └── Dockerfile         
├── proto/                  # Protocol buffer definitions
├── docker-compose.yml      # Docker orchestration
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── tts_test.py             # Test script for TTS
```

---

## ✨ Features
- 🎙️ Convert text into lifelike speech
- ⚙️ Modular architecture with gRPC, REST, and UI layers
- 🚀 Dockerized for easy CI/CD deployment
- 🌐 Streamlit UI and FastAPI backend
- 🔤 SentencePiece for tokenization
- 🧠 Powered by FastSpeech2, Tacotron2, Torchaudio

---

## ⚡ Installation

### 1. Clone the repository
```bash
git clone https://github.com/Rahima411/Story2Audio
cd Story2Audio
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔢 Running the TTS Test Script
Test the TTS functionality and preload models:

```bash
python tts_test.py
```

For verbose logging:
```bash
python tts_test.py --verbose
```

---

## 🚧 Running the Full System

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up --build
```
This starts:
- gRPC TTS server
- REST gateway
- Streamlit frontend

### Option 2: Manual Startup
```bash
# Start the server
cd server
python server.py

# Start the REST gateway
cd ../client
python rest_gateway.py

# Start the frontend
cd ../frontend/streamlit
streamlit run frontend.py
```

---

## 📊 Configuration
- gRPC Server: `server/server.py`
- REST Gateway: `client/rest_gateway.py`
- Frontend: `frontend/streamlit/frontend.py`
- Protobuf Definition: `proto/service.proto`

---

## 🔧 Testing
- Open **Streamlit UI** at: [http://localhost:8501](http://localhost:8501)
- Send **REST API POST** to: `http://localhost:8000/tts`

---

## 🔊 Usage
- Start with Docker Compose
- Access UI on browser
- Input text and click **Generate Speech**
- Playback or download the generated audio

![Demo](docs/demo.gif)

---

## 🔗 Model Sources
- [SpeechT5 – Microsoft (MIT License)](https://huggingface.co/microsoft/speecht5)
- Torchaudio + SentencePiece integration

---

## ⚠ Limitations
- ⚡ Performance may be slow without GPU
- 🌍 Limited language/model support
- 🔊 Audio quality varies by model

---

## 📒 Development Notes
To regenerate gRPC code from `.proto` files:
```bash
python -m grpc_tools.protoc -Iproto --python_out=common --grpc_python_out=common proto/service.proto
```

Use `tts_test.py` to preload models for faster startup.

---

## 🤝 Contributing
Pull requests are welcome! To contribute:

1. Fork the repo  
2. Create a feature branch: `git checkout -b feature/your-feature`  
3. Commit: `git commit -am 'Add feature'`  
4. Push: `git push origin feature/your-feature`  
5. Open a pull request

For significant changes, please open an issue first.

---

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Note: This project uses third-party models (e.g., SpeechT5 by Microsoft) licensed under their respective terms. Please ensure compliance with each model’s license.

```

---