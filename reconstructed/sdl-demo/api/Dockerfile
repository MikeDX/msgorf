# API image — includes WASM headless verifier (same float model as the web game).
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
COPY msgorf_verify.js msgorf_verify.wasm ./

ENV PYTHONUNBUFFERED=1
ENV MSGORF_SERVE_WEB=0
ENV MSGORF_VERIFY=node
ENV MSGORF_VERIFY_SCRIPT=/app/msgorf_verify.js
EXPOSE 8091

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8091"]
