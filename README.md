# Project Backend

Simple FastAPI backend with MySQL authentication—**signup** and **login**. Each teammate can run it locally; ideal for development and for later load testing (e.g. Locust, JMeter, k6) in SENG 533.

---

## Setup

1. Install MySQL
2. Run **database_setup.sql** (in MySQL Workbench or CLI)
3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Update the database password in **app/database.py** (see [How to run](#how-to-run-the-project-teammates--ta) below)
5. Start server

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open

   **http://127.0.0.1:8000/docs**

---

## Repo structure

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

`database_setup.sql` creates the `userdb` database and `users` table so anyone can get the same schema with one run in MySQL Workbench.

---

## How to run the project (teammates / TA)

Follow these steps once per machine.

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd Project-Backend
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs: **fastapi**, **uvicorn**, **mysql-connector-python**, **passlib[bcrypt]**.

### 3. Install MySQL

Install **MySQL Server** on your machine, then open **MySQL Workbench** (or any MySQL client).

### 4. Run the database setup script

In MySQL Workbench (or CLI), open and run:

**`database_setup.sql`**

It creates the database and table:

- Database: `userdb`
- Table: `users` (id, username, email, password, pictureURL, userDescriptionURL)

Run the whole file once. Database is ready.

### 5. Set your database password

Edit **`app/database.py`** and set the connection to match your local MySQL user and password:

```python
mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password_here",
    database="userdb"
)
```

The password will be different on each laptop.

### 6. Start the backend

```bash
uvicorn app.main:app --reload
```

Then open:

**http://127.0.0.1:8000/docs**

Swagger UI loads. You can try:

- **POST /signup** — register a user  
- **POST /login** — authenticate

---

## Setup checklist (quick reference)

1. Install MySQL Server  
2. Run **database_setup.sql** in MySQL Workbench (or CLI)  
3. Install Python deps: `pip install -r requirements.txt`  
4. Update the database password in **app/database.py**  
5. Start server: `uvicorn app.main:app --reload`  
6. Open **http://127.0.0.1:8000/docs**

---

## API endpoints

| Method | Path    | Description        |
|--------|---------|--------------------|
| POST   | /signup | Register a user    |
| POST   | /login  | Authenticate user  |

---

## SENG 533 note

This layout lets every teammate run the backend locally with the same schema. You can point load-testing tools (Locust, JMeter, k6) at `http://127.0.0.1:8000` for performance evaluation.
