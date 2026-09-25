# Production Reproducibility Dockerfile for AIJ / ICAPS Artifact Evaluation
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-dev \
    build-essential cmake clingo \
    git wget nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Clone and build FastLAS ASP Solver from source
RUN git clone https://github.com/spike-imperial/FastLAS.git /opt/FastLAS \
    && cd /opt/FastLAS \
    && mkdir -p build && cd build \
    && cmake .. && make \
    && cp FastLAS /usr/local/bin/

# Clone and install FAMA meta_planning library from source
RUN git clone https://github.com/daineto/meta-planning.git /opt/meta-planning \
    && cd /opt/meta-planning \
    && pip3 install -e .

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

ENV PYTHONPATH=/app

CMD ["python3", "main.py"]
