FROM python:3.10

WORKDIR /app

# Copy shared proto files from root/common/
COPY common/ common/

# Copy the server code, model directory and requiremnets.txt
COPY server/ .
COPY models/ models/
COPY requirements.txt .

RUN pip install --default-timeout=100 --retries=10 --no-cache-dir -r ./requirements.txt

CMD ["python", "server.py"]
