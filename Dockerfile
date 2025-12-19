FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir pyrogram tgcrypto

CMD ["python", "bot.py"]
