FROM python:3.12-slim

WORKDIR /app

# Don't write .pyc files; show print/log output immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies first, so this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
