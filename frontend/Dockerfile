FROM python:3.10

WORKDIR /app

COPY frontend/ .

RUN mkdir -p /root/.streamlit
COPY frontend/.streamlit/config.toml /root/.streamlit/config.toml

COPY assets /app/assets/

RUN pip install --no-cache-dir streamlit requests streamlit-lottie

CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
