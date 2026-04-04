# ProfileHub — SENG 533 (Software Performance Evaluation)

Monorepo for **ProfileHub**: a small full-stack app (Flask + React) with **MySQL**, **Google Cloud Storage** for profile assets, and **Locust** load tests. Use this README as the single entry point; deeper docs live in linked files below.

---

## Repository layout

```
Full - Project/
├── README.md                 ← this file
├── DEPLOY.md                 ← Google Cloud Run deployment (gcloud --source)
├── Dockerfile                ← container image for the backend
├── .dockerignore             ← excludes frontend, load_tests, secrets from images
├── run.bat                   ← Windows: start backend + frontend in two windows
├── .env                      ← create locally (gitignored) — see Environment variables
│
├── backend/                  ← Flask API
│   ├── app.py
│   ├── requirements.txt
│   ├── routes/               ← auth, user CRUD, profile photo & description
│   ├── database/             ← MySQL + connection pool (Database.py)
│   ├── cloudStorage/         ← GCS uploads + signed URLs for private buckets
│   └── utils/config.py       ← loads monorepo root .env
│
├── frontend/                 ← React (Vite) SPA
│   ├── src/
│   ├── vite.config.ts        ← dev proxy /auth and /user → Flask :5000
│   └── .env.example          ← optional VITE_API_URL override
│
└── load_tests/               ← Locust + experiment matrix + analysis
    ├── README.md             ← how to run Locust & analyze CSVs
    ├── locustfile.py
    ├── run_matrix.py
    ├── analyze_results.py
    └── requirements-locust.txt
```

There is **one** `.gitignore` at the repository root (covers backend, frontend, and load-test outputs).

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| **Python 3.12+** | Backend + load tests |
| **Node.js 20+** | Frontend build/dev |
| **MySQL** | User data (local or Cloud SQL) |
| **Google Cloud project** | GCS bucket + (optional) Cloud Run |
| **Service account JSON** (local dev) | Placed under `credentials/` (gitignored); path set in `.env` |

---

## Environment variables

Create a file **`.env` in the monorepo root** (same folder as this `README.md`). It is **gitignored** — do not commit it.

| Variable | Description |
|----------|-------------|
| `DATABASE_HOST` | MySQL host (e.g. `127.0.0.1` or Cloud SQL IP / proxy) |
| `DATABASE_USER` | MySQL user |
| `DATABASE_PASSWORD` | MySQL password |
| `DATABASE_NAME` | Database name |
| `DATABASE_PORT` | Port (default `3306`) |
| `DB_POOL_SIZE` | MySQL pool size; `0` disables pooling (default `10`) |
| `GCS_BUCKET` | Google Cloud Storage bucket name for uploads |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON (local dev). On **Cloud Run**, omit — use the runtime service account. |

Frontend: **`VITE_*`** variables are read from the **monorepo root** (`envDir` in Vite). For local dev, leave `VITE_API_URL` **unset** so the Vite **proxy** sends `/auth` and `/user` to `http://127.0.0.1:5000`. To call the API directly (no proxy), set e.g. `VITE_API_URL=http://127.0.0.1:5000` in `.env`.

---

## Local development

### Option A — Windows (`run.bat`)

From the repo root, double-click or run:

```bat
run.bat
```

This opens two terminals: **Flask** on `http://127.0.0.1:5000` and **Vite** on `http://localhost:3000`.

### Option B — Manual

**Terminal 1 — backend**

```bash
cd backend
python -m venv .venv          # first time only
.venv\Scripts\activate      # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Terminal 2 — frontend**

```bash
cd frontend
npm install                   # first time only
npm run dev
```

Open the app at **http://localhost:3000**.

---

## API overview (Flask)

| Area | Prefix | Notes |
|------|--------|--------|
| Auth | `/auth` | `POST /signup`, `POST /login` |
| User | `/user` | `GET/PATCH/DELETE /<email>`, profile photo & description subroutes |

Profile images and description JSON use **signed GET URLs** in API responses when the bucket is private. The database still stores the canonical `https://storage.googleapis.com/...` object URL.

---

## Load testing (Locust)

Load tests hit the **API only** (no browser). They live in **`load_tests/`**.

1. Start the backend (local or deployed URL).
2. Install Locust deps: `pip install -r load_tests/requirements-locust.txt`
3. Run from **`load_tests/`** — see **[load_tests/README.md](load_tests/README.md)** for:
   - `--host` (**must** be a real URL: `http://127.0.0.1:5000` locally, or your **exact** Cloud Run `https://...run.app` URL — not a placeholder)
   - `run_matrix.py` matrix and `analyze_results.py` statistics

Generated CSVs and analysis output are under `load_tests/results/` and `load_tests/analysis/` (gitignored).

---

## Deployment (Google Cloud Run)

Step-by-step commands (including `gcloud run deploy --source .`, Cloud SQL, env vars, Locust against the deployed URL) are in **[DEPLOY.md](DEPLOY.md)**.

---

## Security notes

- **Never commit** `.env` or `credentials/*.json`.
- For production / Cloud Run, inject secrets via **GCP Secret Manager** or Cloud Run env configuration, not baked into images.

---

## Course context

This project supports **SENG 533 — Software Performance Evaluation** (experiment design, load testing, statistical analysis in the report). The graded deliverables are defined by the course; this repository provides the **implementation and measurement tooling**.
