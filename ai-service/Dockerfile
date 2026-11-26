# QUALIFIL AI service - development image.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (cache-friendly ordering).
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 8001

# The port can be overridden through AI_SERVICE_PORT.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${AI_SERVICE_PORT:-8001}"]
