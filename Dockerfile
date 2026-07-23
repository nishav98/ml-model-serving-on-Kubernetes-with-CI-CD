FROM python:3.11-slim

WORKDIR /code

# Install deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code + trained model bundle
COPY app/ ./app/

EXPOSE 8000

# Basic container-level healthcheck (in addition to K8s probes later)
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
