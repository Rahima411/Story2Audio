import grpc

from common import service_pb2, service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.TTSServiceStub(channel)
        request = service_pb2.TextRequest(text="Hello, this is a test.")
        response = stub.Generate(request)
        print(f"Received audio format: {response.format}")
        print(f"Audio bytes: {response.audio_data}")

if __name__ == '__main__':
    run()
