import grpc
from concurrent import futures
import time
import logging
import os
from common import service_pb2, service_pb2_grpc
# Import health service
from grpc_health.v1 import health_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health

# Configure logging before any other operations
log_dir = os.environ.get("LOG_DIR", "./server/logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, "server.log"))
    ]
)
logger = logging.getLogger("tts_server")

# Fix the imports by ensuring proper order
from text_preprocessing import preprocess_for_tts
from tts_engine import TextToSpeechEngine

# Lazy model loading in worker scope
tts_engine = None

class TTSServiceServicer(service_pb2_grpc.TTSServiceServicer):
    def Generate(self, request, context):
        global tts_engine
        logger.info(f"[gRPC Server] Received: text='{request.text[:50]}...', voice='{request.voice or 'default'}'")

        try:
            audio, chunks, elapsed = tts_engine.generate(request.text, voice=request.voice)
            logger.info(f"Generated {len(audio)} bytes of audio in {elapsed:.2f}s")
            return service_pb2.AudioReply(
                audio_data=audio,
                format="wav",
                chunks=chunks,
                time_taken=elapsed
            )
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}", exc_info=True)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AudioReply()

    def StreamGenerate(self, request, context):
        global tts_engine
        logger.info(f"Received StreamGenerate request: text='{request.text[:50]}...', voice='{request.voice or 'default'}'")
        
        try:
            # First, preprocess the text into chunks
            text_chunks = preprocess_for_tts(request.text)
            if not text_chunks:
                context.set_details("No valid text chunks after preprocessing")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return
            
            # Get voice embedding once to reuse for all chunks
            voice_id = tts_engine.voice_map.get(request.voice, "slt")
            
            start_time = time.time()
            chunk_index = 0
            
            # Process each text chunk separately and stream results
            for text_chunk in text_chunks:
                chunk_start = time.time()
                
                # Generate audio for this chunk
                audio_chunk, _, chunk_elapsed = tts_engine.generate_single_chunk(
                    text_chunk, 
                    voice=voice_id
                )
                
                chunk_index += 1
                logger.debug(f"Generated chunk {chunk_index}/{len(text_chunks)} in {chunk_elapsed:.2f}s")
                
                # Stream this chunk back to the client
                yield service_pb2.AudioReply(
                    audio_data=audio_chunk,
                    format="wav",
                    chunks=[text_chunk],
                    time_taken=chunk_elapsed,
                    chunk_index=chunk_index,
                    total_chunks=len(text_chunks)
                )
                
            total_elapsed = time.time() - start_time
            logger.info(f"Completed streaming {len(text_chunks)} chunks in {total_elapsed:.2f}s")

        except Exception as e:
            logger.error(f"Error in streaming audio generation: {str(e)}", exc_info=True)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return

    def ChatTTS(self, request_iterator, context):
        global tts_engine
        logger.info("Received ChatTTS request stream")
        
        try:
            message_count = 0
            
            for request in request_iterator:
                message_count += 1
                logger.info(f"Processing message {message_count}: text='{request.text[:50]}...', voice='{request.voice or 'default'}'")
                
                if not request.text.strip():
                    logger.warning("Skipping empty message")
                    continue
                
                # Generate audio for this message
                audio, chunks, elapsed = tts_engine.generate(request.text, voice=request.voice)
                
                logger.info(f"Generated response for message {message_count} in {elapsed:.2f}s")
                
                # Send back the audio reply
                yield service_pb2.AudioReply(
                    audio_data=audio,
                    format="wav",
                    chunks=chunks,
                    time_taken=elapsed,
                    message_id=request.message_id if hasattr(request, 'message_id') else str(message_count)
                )
                
            logger.info(f"Completed ChatTTS session with {message_count} messages")
            
        except Exception as e:
            logger.error(f"Error in ChatTTS session: {str(e)}", exc_info=True)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return

def serve():
    global tts_engine

    # Create TTS engine instance
    max_workers = int(os.environ.get("MAX_WORKERS", "10"))
    model_dir = os.environ.get("MODEL_DIR", "./models")

    logger.info(f"Initializing TTS engine with model directory: {model_dir}")
    tts_engine = TextToSpeechEngine(model_dir=model_dir)

    # Set up server with thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    service_pb2_grpc.add_TTSServiceServicer_to_server(TTSServiceServicer(), server)

    # Configure server address
    port = os.environ.get("PORT", "50051")
    server_address = f"[::]:{port}"
    server.add_insecure_port(server_address)

    # Start the server
    logger.info(f"Starting gRPC server on port {port} with {max_workers} workers")
    server.start()

    # Add health service
    health_service = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_service, server)

    # Register health status
    health_service.set('tts.TTSService', health_pb2.HealthCheckResponse.SERVING)

    logger.info("Server started successfully")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()