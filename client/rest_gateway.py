from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import grpc
import base64

from common import service_pb2, service_pb2_grpc

app = FastAPI()


class TextInput(BaseModel):
    text: str


@app.post("/generate")
def generate_tts(request: TextInput):
    try:
        with grpc.insecure_channel('server:50051') as channel:
            stub = service_pb2_grpc.TTSServiceStub(channel)
            grpc_request = service_pb2.TextRequest(text=request.text)
            grpc_response = stub.Generate(grpc_request)
            b64_audio = base64.b64encode(grpc_response.audio_data).decode("utf-8")
            return {
                "format": grpc_response.format,
                "audio_data": b64_audio
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))