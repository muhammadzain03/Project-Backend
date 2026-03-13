# Project Backend

Flask backend with MySQL authentication. Supports user signup, login, and profile management. Each teammate runs it locally — ideal for development and load testing (Locust, JMeter, k6) in SENG 533.

---

## Repo Structure

```

.
└── Project-Backend
    │ 
    ├── app.py
    │ 
    ├── cloudStorage
    │   ├── __init__.py
    │   ├── GCP.py
    │   └── userInfoStorage.py
    │ 
    ├── credentials
    │   └── seng533-490008-98ae5a3775f1.json
    │ 
    ├── database
    │   ├── __init__.py
    │   ├── Database.py
    │   └── dbQueries.py
    │ 
    ├── requirements.txt
    │ 
    ├── routes
    │   ├── __init__.py
    │   ├── authroutes.py
    │   ├── GetUserInfoRoutes.py
    │   └── UpdateUserInfo.py
    │ 
    ├── services
    │   ├── __init__.py
    │   ├── authServices.py
    │   ├── GCPservices.py
    │   └── userServices.py
    │ 
    └── utils
        ├── __init__.py
        └── config.py

```

---

## How to Run

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd Project-Backend
```

### 2. Install Python dependencies

- (Optional) Make a virtual environment

```bash
pip install -r requirements.txt
```

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
GOOGLE_APPLICATION_CREDENTIALS=credentials/your-key.json (Ask for the key form Bilal or Zain)
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

| Method | Path         | Body                                                     | Description       |
| ------ | ------------ | -------------------------------------------------------- | ----------------- |
| POST   | /auth/signup | `{"email": "...", "username": "...", "password": "..."}` | Register a user   |
| POST   | /auth/login  | `{"email": "...", "password": "..."}`                    | Authenticate user |

### Get User Info

| Method | Path                          | Body | Description              |
| ------ | ----------------------------- | ---- | ------------------------ |
| GET    | /user/{email}                 | —    | Get user profile         |
| DELETE | /user/{email}                 | —    | Delete user              |
| GET    | /user/id/{email}              | —    | Get user ID              |
| GET    | /user/profile-url/{email}     | —    | Get user profile URL     |
| GET    | /user/description-url/{email} | —    | Get user description URL |

### Update User Info

| Method | Path                   | Body                            | Description             |
| ------ | ---------------------- | ------------------------------- | ----------------------- |
| POST   | /<email>/profile-photo | form-data, key=file & type=File | Upload user profile pic |
| DELETE | /<email>/profile-photo | —                               | Delete user profile pic |
| POST   | /<email>/description   | `{ "description": "..." }`      | Upload user description |
| DELETE | /<email>/description   | —                               | Delete user description |

###

---

## Architecture

```
Request → routes/ → services/ → storage/dbQueries.py → storage/Database.py → MySQL
```

- **routes/** — HTTP layer. Parses requests, validates input, returns JSON responses.
- **services/** — Business logic. No HTTP knowledge.
- **database/Database.py** — MySQL connection using `.env` credentials.
- **database/dbQueries.py** — All raw SQL queries.
- **cloudStorage/GCP.py** — Google Cloud Storage connection for file uploads.
- **cloudStorage/userInfoStorage.py** - Functions to Upload/Delete user data on GCP Bucket
- **utils/config.py** — Loads `.env` and exposes all config values.

---

## SENG 533 Note

Every teammate runs the backend locally with the same schema. Point load-testing tools (Locust, JMeter, k6) at `http://127.0.0.1:5000` for performance evaluation — measure response time, throughput, and latency at 10 / 100 / 250 concurrent users.
