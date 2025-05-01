FROM python:3.10

WORKDIR /app

COPY frontend/ .

RUN pip install --no-cache-dir streamlit requests

CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
