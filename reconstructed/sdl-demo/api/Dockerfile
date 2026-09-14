FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .

ENV PYTHONUNBUFFERED=1
ENV MSGORF_SERVE_WEB=0
EXPOSE 8091

# Bind all interfaces for Traefik / docker networking.
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8091"]
