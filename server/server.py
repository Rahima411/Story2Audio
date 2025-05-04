import grpc
from concurrent import futures
import time

from common import service_pb2, service_pb2_grpc
from tts_engine import TextToSpeechEngine

# Lazy model loading in worker scope
tts_engine = None

class TTSServiceServicer(service_pb2_grpc.TTSServiceServicer):
    def Generate(self, request, context):
        global tts_engine
        print(f"[gRPC Server] Received: text='{request.text[:50]}...', voice='{request.voice or 'default'}'")
        
        try:
            audio, chunks, elapsed = tts_engine.generate(request.text, voice=request.voice)
            return service_pb2.AudioReply(
                audio_data=audio,
                format="wav",
                chunks=chunks,
                time_taken=elapsed
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AudioReply()

    def StreamGenerate(self, request, context):
        # Stub
        yield service_pb2.AudioReply(audio_data=b'\x01\x02\x03', format="wav")

    def ChatTTS(self, request_iterator, context):
        # Stub
        for request in request_iterator:
            yield service_pb2.AudioReply(audio_data=b'\x05\x06\x07', format="wav")

def serve():
    global tts_engine
    tts_engine = TextToSpeechEngine()  # Load per process
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TTSServiceServicer_to_server(TTSServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[gRPC Server] Running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
