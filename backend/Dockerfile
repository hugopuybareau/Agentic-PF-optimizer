FROM python:3.13.2-slim

WORKDIR /backend

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(uname -m) && \
    case "$ARCH" in \
      x86_64) UVURL="https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz"; UVDIR="uv-x86_64-unknown-linux-gnu";; \
      aarch64) UVURL="https://github.com/astral-sh/uv/releases/latest/download/uv-aarch64-unknown-linux-gnu.tar.gz"; UVDIR="uv-aarch64-unknown-linux-gnu";; \
      *) echo "Unsupported arch: $ARCH"; exit 1;; \
    esac && \
    curl -L $UVURL -o /tmp/uv.tar.gz && \
    tar -xzvf /tmp/uv.tar.gz -C /tmp && \
    mv /tmp/$UVDIR/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv && \
    rm -rf /tmp/uv*

RUN uv --version

COPY backend/requirements.txt ./requirements.txt
COPY backend/wait-for-it.sh ./wait-for-it.sh

RUN chmod +x ./wait-for-it.sh

RUN uv venv .venv

RUN /usr/local/bin/uv pip install --upgrade pip && \
    /usr/local/bin/uv pip install -r requirements.txt && \
    ls -l .venv/bin

COPY backend /backend

ENV VIRTUAL_ENV="/backend/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000