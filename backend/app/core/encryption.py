"""
Encryption utility for securely storing sensitive OAuth tokens.
Uses cryptography.fernet for symmetric encryption.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import get_settings
from app.core import get_logger

logger = get_logger(__name__)
settings = get_settings()

_fernet_instance: Fernet | None = None


def _get_encryption_key() -> bytes:
    """Derive or load the encryption key."""
    # Check if a fixed key is provided via .env
    env_key = getattr(settings, "ENCRYPTION_KEY", None)
    if env_key:
        if len(env_key) == 44:  # Base64 standard length for Fernet
            return env_key.encode("utf-8")
        else:
            # Derive a valid Fernet key from the string
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"autotransai_salt_123",
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(env_key.encode("utf-8")))
            return key

    # Generate or read persistent local key if no env key
    key_path = settings.DATA_DIR / ".encryption_key"
    if key_path.exists():
        with open(key_path, "rb") as f:
            return f.read().strip()
            
    # Generate new
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    new_key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(new_key)
    logger.info("Generated new local encryption key.")
    return new_key


def _get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is None:
        key = _get_encryption_key()
        _fernet_instance = Fernet(key)
    return _fernet_instance


def encrypt_data(data: str) -> str:
    """Encrypt a string."""
    if not data:
        return data
    f = _get_fernet()
    encrypted = f.encrypt(data.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt a string."""
    if not encrypted_data:
        return encrypted_data
    f = _get_fernet()
    try:
        decrypted = f.decrypt(encrypted_data.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt data: {e}")
        return ""
