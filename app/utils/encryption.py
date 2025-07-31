from cryptography.fernet import Fernet
import base64
import os
from typing import Optional


# Generate a key from environment variable or create/load a persistent one
ENCRYPTION_KEY_FILE = ".encryption_key"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

if not ENCRYPTION_KEY:
    # Try to load from file
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, "r") as f:
            ENCRYPTION_KEY = f.read().strip()
    else:
        # Generate a new key and save it
        ENCRYPTION_KEY = Fernet.generate_key().decode()
        with open(ENCRYPTION_KEY_FILE, "w") as f:
            f.write(ENCRYPTION_KEY)
        print(f"Generated new encryption key and saved to {ENCRYPTION_KEY_FILE}")

fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_password(plain_password: str) -> str:
    """
    Encrypt a plain text password.
    """
    encrypted = fernet.encrypt(plain_password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str) -> Optional[str]:
    """
    Decrypt an encrypted password.
    """
    try:
        decrypted = fernet.decrypt(encrypted_password.encode())
        return decrypted.decode()
    except Exception:
        return None