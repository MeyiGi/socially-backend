from datetime import datetime, timedelta
from jose import jwt
import bcrypt  # Use bcrypt directly instead of passlib
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt.checkpw requires bytes
    password_byte = plain_password.encode('utf-8')
    
    # Ensure hashed_password is bytes (it might come as str from DB)
    if isinstance(hashed_password, str):
        hashed_password_byte = hashed_password.encode('utf-8')
    else:
        hashed_password_byte = hashed_password

    return bcrypt.checkpw(password_byte, hashed_password_byte)

def get_password_hash(password: str) -> str:
    # bcrypt.hashpw requires bytes and returns bytes
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)