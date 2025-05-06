# Story2Audio System

This project is a Text-to-Speech (TTS) system with a modular architecture, including a frontend (Streamlit), backend (FastAPI), and gRPC services for communication between components. The system converts text input into speech output using pre-trained TTS models.

## Architecture
```
├── client/                  # gRPC client implementation
├── common/                  # Shared protobuf/gRPC files
├── frontend/                # Streamlit web interface
│   ├── streamlit/           # Streamlit app files
├── server/                  # TTS server implementation
│   ├── text_preprocessing.py # Text normalization
│   └── tts_engine.py        # Core TTS functionality
├── proto/                   # Protocol buffer definitions
├── venv/                    # Python virtual environment
├── docker-compose.yml       # Docker orchestration
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── tts_test.py              # Test script for TTS 
```
---

## Prerequisites
- Docker and Docker Compose

- Python 3.8+

- *(Optional)* NVIDIA Docker for GPU acceleration

## Installation
### 1.Clone the repository:

```bash
git clone <https://github.com/Rahima411/Story2Audio>
cd Story2Audio
```
### 2.Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.Install dependencies:

```bash
pip install -r requirements.txt
```
---

## Running the TTS Test Script

Run `tts_test.py` to test TTS functionality and preload model embeddings:

```bash
python tts_test.py
```

This will:
- Load necessary TTS models and embeddings
- Process sample text inputs
- Generate audio outputs
- Provide performance metrics

### For verbose output:
```bash
python tts_test.py --verbose
```

## Running the Full System
### Option 1: Docker Compose (Recommended)
```bash
docker-compose up --build
```
This will start:
- The gRPC TTS server
- The REST gateway
- The Streamlit frontend

### Option 2: Manual Startup
#### Start the gRPC server:
```bash
cd server
python server.py
```
#### Start the REST gateway:
```bash
cd ../client
python rest_gateway.py
```
#### Start the frontend:
```bash
cd ../frontend/streamlit
streamlit run frontend.py
```

---

## Configuration
- Server: `server/server.py`
- Frontend: `frontend/streamlit/frontend.py`
- Protocol Buffers: `proto/service.proto`

---

## Testing

After starting the services:
- Access the **Streamlit UI**: [http://localhost:8501](http://localhost:8501)
- Send REST API requests: `POST http://localhost:8000/tts`

---

## Usage

- Start all services with Docker Compose
- Open the Streamlit frontend
- Enter your text and click “Generate Speech”
- Listen to or download the generated audio

---

## Model Sources

This system uses:
- Transformers-based TTS models (e.g., FastSpeech2, Tacotron2)
- SentencePiece for tokenization
- Torchaudio for audio processing
- Pre-trained models from Hugging Face

---

## Limitations

- **Performance**: Inference may be slow without GPU
- **Language support**: Limited to supported models
- **Audio quality**: Depends on the chosen model
- **Text length**: Long texts may need to be split
- **Special characters**: Handling may vary

---

## Development Notes

To regenerate gRPC Python code from `.proto` files:
```bash
python -m grpc_tools.protoc -Iproto --python_out=common --grpc_python_out=common proto/service.proto
```

Use `tts_test.py` to verify TTS functionality and cache models for faster startup.

---