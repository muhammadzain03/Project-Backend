# API endpoints (signup/login)

from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas import UserSignup, UserLogin
from app.utils import hash_password, verify_password

router = APIRouter()

@router.post("/signup")
def signup(user: UserSignup):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (user.username,)
    )

    existing = cursor.fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users (username, email, password, pictureURL, userDescriptionURL)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            user.username,
            user.email,
            hashed_pw,
            user.pictureURL,
            user.userDescriptionURL
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserLogin):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = %s",
        (user.username,)
    )

    existing = cursor.fetchone()

    if not existing:
        raise HTTPException(status_code=400, detail="Invalid username")

    stored_password = existing[0]

    if not verify_password(user.password, stored_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    cursor.close()
    conn.close()

    return {"message": "Login successful"}
