import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# load env variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 24))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ------------------ Create Token ------------------ #
def create_access_token(data: dict, expires_delta: timedelta | None = None):

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables")

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# ------------------ Verify Token ------------------ #
def verify_token(token: str = Depends(oauth2_scheme)):

    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail="Server misconfiguration")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "user_id": user_id,
            "email": email
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")