# Project Backend

Flask backend with MySQL authentication. Supports user signup, login, and profile management. Each teammate runs it locally — ideal for development and load testing (Locust, JMeter, k6) in SENG 533.

---

## Repo Structure

```
Project-Backend/
├── routes/
│   ├── authroutes.py        # POST /auth/signup, POST /auth/login
│   └── userRoutes.py        # GET/DELETE /user/{email}, profile/description URL endpoints
├── services/
│   ├── authServices.py      # Auth business logic
│   └── userServices.py      # User data operations
├── storage/
│   ├── Database.py          # MySQL connection
│   ├── dbQueries.py         # All raw SQL queries
│   └── GCP.py               # Google Cloud Storage connection
├── utils/
│   └── config.py            # Reads credentials from .env
├── credentials/             # GCP service account key (NOT committed)
│   └── gcp-key.json
├── app.py                   # Flask app entry point
├── database_setup.sql       # Creates userdb and users table
├── requirements.txt
├── .env                     # Local credentials (NOT committed)
└── .gitignore
```

---

## How to Run

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd Project-Backend
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Installs: **flask**, **mysql-connector-python**, **bcrypt**, **python-dotenv**, **google-cloud-storage**.

### 3. Install MySQL

Install **MySQL Server**, then open **MySQL Workbench** (or any MySQL client).

### 4. Run the database setup script

Open and run **`database_setup.sql`** in MySQL Workbench (or CLI).

Creates:
- Database: `userdb`
- Table: `users` (id, username, email, password, pictureURL, userDescriptionURL)

Run once. Done.

### 5. Create your .env file

Create a `.env` file in the project root:

```env
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_password_here
DATABASE_NAME=userdb
DATABASE_PORT=3306

GCS_BUCKET=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=credentials/your-key.json
```

Password will differ on each machine. Leave GCS fields empty if not using Google Cloud yet.

### 6. Start the server

From the **Project-Backend** folder:

```bash
python app.py
```

Server runs at **http://127.0.0.1:5000**

---

## API Endpoints

### Auth

| Method | Path          | Body                              | Description       |
|--------|---------------|-----------------------------------|-------------------|
| POST   | /auth/signup  | `{email, username, password}`     | Register a user   |
| POST   | /auth/login   | `{email, password}`               | Authenticate user |

### User

| Method | Path                          | Body          | Description              |
|--------|-------------------------------|---------------|--------------------------|
| GET    | /user/{email}                 | —             | Get user profile         |
| DELETE | /user/{email}                 | —             | Delete user              |
| PUT    | /user/{email}/profile-url     | `{url}`       | Update profile picture   |
| DELETE | /user/{email}/profile-url     | —             | Remove profile picture   |
| PUT    | /user/{email}/description-url | `{url}`       | Update description file  |
| DELETE | /user/{email}/description-url | —             | Remove description file  |

---

## Architecture

```
Request → routes/ → services/ → storage/dbQueries.py → storage/Database.py → MySQL
```

- **routes/** — HTTP layer. Parses requests, validates input, returns JSON responses.
- **services/** — Business logic. No HTTP knowledge.
- **storage/dbQueries.py** — All raw SQL queries.
- **storage/Database.py** — MySQL connection using `.env` credentials.
- **utils/config.py** — Loads `.env` and exposes all config values.
- **storage/GCP.py** — Google Cloud Storage connection for file uploads.

---

## SENG 533 Note

Every teammate runs the backend locally with the same schema. Point load-testing tools (Locust, JMeter, k6) at `http://127.0.0.1:5000` for performance evaluation — measure response time, throughput, and latency at 10 / 100 / 250 concurrent users.
