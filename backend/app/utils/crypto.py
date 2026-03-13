import base64

from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.ljust(32)[:32].encode())
    return Fernet(key)


def encrypt_token(token: str) -> str:
    return _get_fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()
