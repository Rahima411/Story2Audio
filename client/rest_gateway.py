from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import grpc
import base64
import time
import traceback
import logging
import os
import io
from typing import List

from common import service_pb2, service_pb2_grpc

log_dir = os.environ.get("LOG_DIR", ".client/logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.environ.get("LOG_DIR", "/logs"), "rest_gateway.log"))
    ]
)
logger = logging.getLogger("rest_gateway")

app = FastAPI(
    title="TTS API",
    description="Text-to-Speech API for generating audio from text",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and response models
class TextInput(BaseModel):
    text: str = Field(..., description="The text to convert to speech", example="Hello, world!")
    voice: str = Field("Default", description="The voice to use for synthesis")

class AudioResponse(BaseModel):
    format: str = Field(..., description="Audio format (e.g., 'wav')")
    audio_data: str = Field(..., description="Base64-encoded audio data")
    chunks: List[str] = Field([], description="Text chunks used for synthesis")
    time_taken: float = Field(..., description="Time taken to generate audio in seconds")

# Create a gRPC channel and stub
def get_grpc_stub():
    grpc_server = os.environ.get("GRPC_SERVER", "server:50051")
    try:
        channel = grpc.insecure_channel(grpc_server)
        stub = service_pb2_grpc.TTSServiceStub(channel)
        return stub
    except Exception as e:
        logger.error(f"Failed to create gRPC stub: {str(e)}")
        raise HTTPException(status_code=503, detail="TTS service unavailable")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check endpoint
@app.get("/health", summary="Health Check", tags=["Health"])
async def health_check():
    try:
        stub = get_grpc_stub()
        return {"status": "healthy", "dependencies": {"grpc_server": "up"}}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "dependencies": {"grpc_server": "down"}, "details": str(e)}, 503

# Main generation endpoint
@app.post("/generate", response_model=AudioResponse, summary="Generate speech from text", tags=["TTS"])
def generate_tts(request: TextInput, stub: service_pb2_grpc.TTSServiceStub = Depends(get_grpc_stub)):
    start_time = time.time()

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        logger.info(f"Received TTS request: text='{request.text[:50]}...', voice='{request.voice}'")
        grpc_request = service_pb2.TextRequest(text=request.text, voice=request.voice or "Default")
        
        grpc_response = stub.Generate(grpc_request, timeout=60.0)
        
        b64_audio = base64.b64encode(grpc_response.audio_data).decode("utf-8")
        elapsed = time.time() - start_time

        logger.info(f"Successfully generated audio ({len(grpc_response.audio_data)} bytes) in {elapsed:.2f}s")

        return {
            "format": grpc_response.format,
            "audio_data": b64_audio,
            "chunks": list(grpc_response.chunks),
            "time_taken": grpc_response.time_taken or elapsed
        }

    except grpc.RpcError as rpc_error:
        error_code = rpc_error.code()
        http_status = 500

        if error_code == grpc.StatusCode.INVALID_ARGUMENT:
            http_status = 400
        elif error_code == grpc.StatusCode.NOT_FOUND:
            http_status = 404
        elif error_code == grpc.StatusCode.DEADLINE_EXCEEDED:
            http_status = 504
        elif error_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
            http_status = 429
        elif error_code == grpc.StatusCode.UNAVAILABLE:
            http_status = 503

        logger.error(f"gRPC error {error_code}: {rpc_error.details()}")
        raise HTTPException(status_code=http_status, detail=f"TTS service error: {rpc_error.details()}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Streaming version of the generate endpoint
@app.post("/generate/stream", summary="Stream speech generation", tags=["TTS"])
async def stream_generate_tts(request: TextInput, stub: service_pb2_grpc.TTSServiceStub = Depends(get_grpc_stub)):
    try:
        logger.info(f"Received streaming TTS request: text='{request.text[:50]}...', voice='{request.voice}'")
        grpc_request = service_pb2.TextRequest(text=request.text, voice=request.voice or "Default")

        def audio_stream_generator():
            audio_buffer = io.BytesIO()
            try:
                for response in stub.StreamGenerate(grpc_request):
                    audio_buffer.write(response.audio_data)
                    yield response.audio_data

                logger.info(f"Completed streaming response, total size: {audio_buffer.tell()} bytes")

            except grpc.RpcError as rpc_error:
                logger.error(f"gRPC streaming error: {rpc_error.details()}")

        return StreamingResponse(
            audio_stream_generator(),
            media_type="audio/wav",
            headers={"X-Content-Type-Options": "nosniff"}
        )

    except Exception as e:
        logger.error(f"Error in streaming endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 1))

    logger.info(f"Starting REST gateway on {host}:{port} with {workers} workers")
    uvicorn.run("rest_gateway:app", host=host, port=port, workers=workers)
