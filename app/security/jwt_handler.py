from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status

from app.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data):
    to_encode = {
        "id": data.id,
        "name": data.name,
        "email": data.email
    }
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


