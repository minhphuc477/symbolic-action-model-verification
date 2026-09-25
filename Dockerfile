# Production Reproducibility Dockerfile for Paper 1 Benchmark Suite
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip \
    build-essential cmake \
    git wget nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

ENV PYTHONPATH=/app

CMD ["python3", "main.py"]
