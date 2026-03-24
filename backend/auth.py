from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from database import get_db
from security import create_access_token

router = APIRouter(prefix="", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------ Schemas ------------------ #
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ------------------ Signup ------------------ #
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):

    try:
        # check if user exists
        check_query = text("SELECT id FROM users WHERE email = :email")
        existing_user = db.execute(check_query, {"email": data.email}).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        # hash password
        password_hash = pwd_context.hash(data.password)

        # insert user (no RETURNING for SQLite)
        insert_query = text("""
            INSERT INTO users (email, password_hash)
            VALUES (:email, :password_hash)
        """)

        db.execute(insert_query, {
            "email": data.email,
            "password_hash": password_hash
        })

        db.commit()

        # fetch user
        select_query = text("""
            SELECT id, email FROM users WHERE email = :email
        """)

        user = db.execute(select_query, {"email": data.email}).fetchone()

        return {
            "message": "User created successfully",
            "user_id": str(user.id),
            "email": user.email
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ------------------ Login ------------------ #
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    try:
        query = text("""
            SELECT id, email, password_hash
            FROM users
            WHERE email = :email
        """)

        result = db.execute(query, {"email": data.email})
        user = result.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = create_access_token({
            "sub": str(user.id),
            "email": user.email
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))