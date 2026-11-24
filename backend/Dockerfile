# QUALIFIL backend — development image.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cache-friendly ordering).
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY . /app

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=config.settings.development
ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
