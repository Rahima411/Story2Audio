FROM python:3.10

WORKDIR /app

# Copy shared gRPC files from root/common/ into the container
COPY common/ common/

# Copy everything else in client/ (rest_gateway, etc.)
COPY client/ .

COPY requirements.txt .

RUN pip install --default-timeout=100 --retries=10 --no-cache-dir -r ./requirements.txt

CMD ["uvicorn", "rest_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
