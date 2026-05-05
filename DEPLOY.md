# Cloud Run Deployment Guide – SENG 533

See also the monorepo **[README.md](README.md)** for local setup and repository layout.

## Prerequisites

You already have:
- GCP project `SENG533` (visible in your console)
- Cloud SQL MySQL instance (from your midterm setup)
- GCS bucket `userdata003`

You need:
- [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed on your PC
- Docker is NOT required – Cloud Build builds the image for you in the cloud

---

## Step-by-step deployment

### 1. Authenticate with gcloud

Open a terminal and run:

```bash
gcloud auth login
gcloud config set project SENG533
```

### 2. Enable required APIs (one-time)

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com
```

### 3. Repository layout

This repository already includes **`Dockerfile`**, **`.dockerignore`**, and the backend files at `backend/cloudStorage/GCP.py`, `backend/database/Database.py`, and `backend/utils/config.py`. Deploy from the **monorepo root** (the folder that contains `backend/`, `frontend/`, and `Dockerfile`).

### 4. Find your Cloud SQL connection name

Go to: https://console.cloud.google.com/sql/instances

Click your MySQL instance → look for **Connection name** on the Overview page.
It looks like: `SENG533:us-central1:your-instance-name`

Also note your instance's **Private IP** or **Public IP**.

### 5. Build and deploy

From your monorepo root directory, run this single command (replace the placeholders):

```bash
gcloud run deploy profilehub-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "\
DATABASE_HOST=YOUR_CLOUD_SQL_IP,\
DATABASE_USER=root,\
DATABASE_PASSWORD=YOUR_DB_PASSWORD,\
DATABASE_NAME=userdb,\
DATABASE_PORT=3306,\
GCS_BUCKET=userdata003,\
DB_POOL_SIZE=10" \
  --add-cloudsql-instances SENG533:us-central1:YOUR_INSTANCE_NAME \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 4 \
  --timeout 120
```

**What this does:**
- `--source .` → Cloud Build reads the Dockerfile, builds the image, pushes it to Artifact Registry
- `--allow-unauthenticated` → Locust can hit the endpoints without auth tokens
- `--set-env-vars` → injects your database credentials (no .env file needed in the container)
- `--add-cloudsql-instances` → connects to Cloud SQL via the Cloud SQL Auth Proxy
- `--min-instances 1` → keeps one instance warm (avoids cold-start latency during tests)

### 6. Note your service URL

After deployment, gcloud prints:

```
Service URL: https://profilehub-backend-XXXX-uc.a.run.app
```

Copy this URL – this is what you'll point Locust at.

### 7. Verify it works

```bash
curl https://profilehub-backend-XXXX-uc.a.run.app/auth/login \
  -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"wrong"}'
```

You should get back:
```json
{"message":"Invalid email or password.","success":false}
```

That confirms Flask is running, MySQL is connected, and the endpoint works.

---

## Cloud SQL connection details

If your Cloud SQL instance uses a **Public IP**, set `DATABASE_HOST` to that IP.

If it uses a **Private IP** or the Cloud SQL Auth Proxy (recommended), the proxy
maps the connection to `127.0.0.1`. In that case:

```
DATABASE_HOST=127.0.0.1
```

The `--add-cloudsql-instances` flag auto-starts the proxy sidecar in the Cloud Run container.

---

## Run load tests against Cloud Run

```bash
cd load_tests

# Smoke test
python run_matrix.py \
  --host https://profilehub-backend-XXXX-uc.a.run.app \
  --workloads mixed --sizes small --users 10 --reps 1 --duration 60

# Full matrix
python run_matrix.py \
  --host https://profilehub-backend-XXXX-uc.a.run.app
```

---

## Useful commands

```bash
# View logs
gcloud run services logs read profilehub-backend --region us-central1

# Update env vars without redeploying
gcloud run services update profilehub-backend \
  --region us-central1 \
  --set-env-vars "DB_POOL_SIZE=20"

# Delete the service when done (stop billing)
gcloud run services delete profilehub-backend --region us-central1
```
