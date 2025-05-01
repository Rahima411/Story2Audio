import grpc
from concurrent import futures
import time

from common import service_pb2, service_pb2_grpc

# Define the actual service logic
class TTSServiceServicer(service_pb2_grpc.TTSServiceServicer):
    def Generate(self, request, context):
        print(f"Received text: {request.text}")
        # Dummy audio data
        audio_bytes = b'\x00\x01\x02'  # placeholder bytes
        return service_pb2.AudioReply(audio_data=audio_bytes, format="wav")

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
    print("gRPC server running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
