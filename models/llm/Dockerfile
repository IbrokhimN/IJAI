FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_PROGRESS_BAR=off

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]

# it is the test version idk if it works 
