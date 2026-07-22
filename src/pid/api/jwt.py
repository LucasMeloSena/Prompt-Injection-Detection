import os
from dotenv import load_dotenv

from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from pid.db.connection import get_session_factory, User

load_dotenv()

secret_key = os.getenv("JWT_SECRET_KEY")
algorithm = "HS256"
days_expiration = 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def generate_hash(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
  return pwd_context.verify(password, hashed_password)

def generate_jwt(data: dict) -> str:
  expires_at = datetime.now(UTC) + timedelta(days=days_expiration)
  data.update({"exp": expires_at})

  token = jwt.encode(data, secret_key, algorithm)
  return token

def decode_jwt(token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="It wasn't possible to validate your credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )

  try:
    payload = jwt.decode(token, secret_key, algorithm)
    _id = payload.get("sub")
    email = payload.get("email")
    if _id is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception

  return {"sub": _id, "email": email}

def get_user_by_email(email: str):
  session = get_session_factory()()
  try:
    statement = select(User).where(User.email == email)
    return session.scalars(statement).first()
  finally:
    session.close()