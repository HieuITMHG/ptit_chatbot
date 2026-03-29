from datetime import timedelta, datetime, timezone
from pwdlib import PasswordHash
import jwt

from app.repositories.user_repo import get_user
from core.config import settings

from app.schemas.user import UserInDB

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("thisisadummypassword")
 
def verify_password(plain, hashed):
    return password_hash.verify(plain, hashed)

def decode_token(token: str):
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

def authenticate_user(username: str, password: str):
    user_dict = get_user(username) 

    if not user_dict:
        verify_password(password, DUMMY_HASH)
        return None
    
    user = UserInDB(**user_dict) 

    if not verify_password(password, user.hashed_password):
        return None

    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)