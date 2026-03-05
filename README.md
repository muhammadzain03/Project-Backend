# Project Backend

Simple FastAPI backend with MySQL authentication—**signup** and **login**. Each teammate runs it locally; ideal for development and load testing (Locust, JMeter, k6) in SENG 533.

---

## Repo Structure

```
Project-Backend/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── utils.py
│   └── database.py
├── database_setup.sql
├── requirements.txt
└── README.md
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

Installs: **fastapi**, **uvicorn**, **mysql-connector-python**, **passlib[bcrypt]**.

### 3. Install MySQL

Install **MySQL Server**, then open **MySQL Workbench** (or any MySQL client).

### 4. Run the database setup script

Open and run **`database_setup.sql`** in MySQL Workbench (or CLI).

Creates:
- Database: `userdb`
- Table: `users` (id, username, email, password, pictureURL, userDescriptionURL)

Run once. Done.

### 5. Set your database password

Edit **`app/database.py`**:

```python
mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password_here",
    database="userdb"
)
```

Password will differ on each machine.

### 6. Start the server

From the **Project-Backend** folder:

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs**

Test: **POST /signup** · **POST /login**

---

## API Endpoints

| Method | Path    | Description       |
|--------|---------|-------------------|
| POST   | /signup | Register a user   |
| POST   | /login  | Authenticate user |

---

## SENG 533 Note

Every teammate runs the backend locally with the same schema. Point load-testing tools (Locust, JMeter, k6) at `http://127.0.0.1:8000` for performance evaluation.

---

## Future Testing: Load Simulation

Add a read endpoint to `app/routes.py` to simulate realistic workloads (e.g. 80% reads / 20% writes):

```python
@router.get("/user/{username}")
def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, email, pictureURL, userDescriptionURL FROM users WHERE username = %s",
        (username,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

The backend will then support:

| Method | Path              | Description        |
|--------|-------------------|--------------------|
| POST   | /signup           | Create user        |
| POST   | /login            | Authenticate user  |
| GET    | /user/{username}  | Read user profile  |

Use **Locust** to load test at 10 / 100 / 250 concurrent users and measure **response time**, **throughput**, and **latency** — the core metrics for your SENG 533 project.
