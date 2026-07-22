from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from pid.api.jwt import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
  return decode_jwt(token)
