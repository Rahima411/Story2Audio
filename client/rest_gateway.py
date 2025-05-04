from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import grpc
import base64
import time
import traceback

from common import service_pb2, service_pb2_grpc

app = FastAPI()


class TextInput(BaseModel):
    text: str
    voice: str = "Default"  


@app.post("/generate")
def generate_tts(request: TextInput):
    try:
        with grpc.insecure_channel('server:50051') as channel:
            stub = service_pb2_grpc.TTSServiceStub(channel)

            start_time = time.time()
            grpc_request = service_pb2.TextRequest(text=request.text, voice=request.voice or "Default")
            grpc_response = stub.Generate(grpc_request)

            b64_audio = base64.b64encode(grpc_response.audio_data).decode("utf-8")
            elapsed = time.time() - start_time

            return {
                "format": grpc_response.format,
                "audio_data": b64_audio,
                "chunks": list(grpc_response.chunks),
                "time_taken": grpc_response.time_taken or elapsed
            }

    except grpc.RpcError as rpc_error:
        raise HTTPException(status_code=rpc_error.code().value[0], detail=f"gRPC Error: {rpc_error.details()}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
