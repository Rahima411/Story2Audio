FROM python:3.10

WORKDIR /app

# Copy shared proto files from root/common/
COPY common/ common/

# Copy the server code
COPY server/ .

RUN pip install --no-cache-dir grpcio grpcio-tools soundfile

CMD ["python", "server.py"]
