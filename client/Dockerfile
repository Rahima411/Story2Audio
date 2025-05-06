FROM python:3.10

WORKDIR /app

COPY common/ common/
COPY . .
COPY requirements.txt .

ENV PYTHONPATH=/app

COPY client/ .

RUN pip install --default-timeout=100 --retries=10 --no-cache-dir -r ./requirements.txt

CMD ["uvicorn", "rest_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
