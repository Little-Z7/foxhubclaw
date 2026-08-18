from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet


def _fernet(secret: str) -> Fernet:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(plain: str, secret: str) -> str:
    return _fernet(secret).encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str, secret: str) -> str:
    return _fernet(secret).decrypt(token.encode("utf-8")).decode("utf-8")


def mask_key(key: str) -> str:
    if not key:
        return ""
    tail = key[-4:]
    return f"••••{tail}"
