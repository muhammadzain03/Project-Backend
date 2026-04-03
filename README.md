# SENG 533 — Project

Monorepo layout:

```
SENG 533 - Project/
├── .env                # Your secrets (gitignored) — copy from .env.example
├── .env.example
├── backend/            # Flask API (Python)
├── frontend/           # Vite + React UI
├── credentials/        # GCP key JSON (gitignored)
├── .gitignore
└── README.md
```

**Environment:** Use a single **`.env`** at this folder (not `backend/.env`). Vite reads it via `frontend/vite.config.ts` (`envDir`). Put GCP JSON under **`credentials/`** and set `GOOGLE_APPLICATION_CREDENTIALS=credentials/your-key.json` (paths relative to this folder).

---

## Quick start

**Backend** (from `backend/`):

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server: **http://127.0.0.1:5000**

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/auth` and `/user` to port 5000. **`VITE_API_URL`** in the root `.env` (e.g. `http://127.0.0.1:5000`) points the browser at Flask; **`flask-cors`** allows requests from `localhost:3000` when you use that URL directly.

---

## API (Flask)

| Area | Examples |
|------|----------|
| Auth | `POST /auth/signup`, `POST /auth/login` |
| User | `GET /user/{email}`, `DELETE /user/{email}`, `GET /user/id/{email}`, profile/description URLs |
| Files | `POST/DELETE /user/{email}/profile-photo`, `POST/DELETE /user/{email}/description` |

Align the frontend to these paths and JSON shapes.

---

## SENG 533

Point load-testing tools at **http://127.0.0.1:5000** when the backend is running locally.

---

## Old duplicate trees

If you still have another copy of the backend elsewhere, diff against **`backend/`** here, keep one canonical tree, and delete the duplicate once you are sure nothing unique is lost.
