# -- SENG 533 – ProfileHub Backend ------------------------------------
# Build:  gcloud builds submit --tag gcr.io/PROJECT_ID/profilehub-backend
# Deploy: gcloud run deploy profilehub-backend --image gcr.io/PROJECT_ID/profilehub-backend ...

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Keep backend/ as a subfolder so backend/utils/config.py parents[2] == /app (monorepo root)
WORKDIR /app
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend

WORKDIR /app/backend
ENV PYTHONPATH=/app/backend

# Cloud Run sets PORT env var (default 8080)
ENV PORT=8080

# Use gunicorn for production (Flask dev server is single-threaded)
# 4 workers + 2 threads each = 8 concurrent request handlers
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 4 --threads 2 --timeout 120 app:app"]
