from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import os
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT access token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


# Encryption functions
def get_encryption_key() -> bytes:
    """Get or create encryption key"""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate a new key for development
        key = Fernet.generate_key()
        print(f"Generated new encryption key: {key.decode()}")
        return key
    return key.encode()


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return ""

    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""

    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception:
        # Return empty string if decryption fails
        return ""
