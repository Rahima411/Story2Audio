import grpc
from concurrent import futures
import time
import io
import soundfile as sf
import numpy as np
from fastapi import HTTPException

from common import service_pb2, service_pb2_grpc

from common.text_preprocessing import preprocess_for_tts  # Add this if you want to preprocess

class TTSServiceServicer(service_pb2_grpc.TTSServiceServicer):
    def Generate(self, request, context):
        print(f"[gRPC Server] Received text: {request.text}")
        start_time = time.time()

        # Optional: Preprocess
        chunks = preprocess_for_tts(request.text)

        if not chunks:
            raise HTTPException(status_code=400, detail="No valid text after preprocessing.")

        final_audio = b""

        for chunk in chunks:
            # Generate a sine wave as dummy audio
            duration = 1.0  # seconds
            samplerate = 16000  # Hz
            t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
            freq = 440  # A4 note
            audio = 0.5 * np.sin(2 * np.pi * freq * t)

            # Save to WAV in-memory
            buffer = io.BytesIO()
            sf.write(buffer, audio, samplerate, format='WAV')
            audio_bytes = buffer.getvalue()
            final_audio += audio_bytes

        elapsed = time.time() - start_time

        return service_pb2.AudioReply(audio_data=final_audio, format="wav", chunks=chunks, time_taken=elapsed)

    def StreamGenerate(self, request, context):
        for i in range(3):
            yield service_pb2.AudioReply(audio_data=b'\x01\x02\x03', format="wav")
            time.sleep(1)

    def ChatTTS(self, request_iterator, context):
        for request in request_iterator:
            yield service_pb2.AudioReply(audio_data=b'\x05\x06\x07', format="wav")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TTSServiceServicer_to_server(TTSServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[gRPC Server] Running on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
