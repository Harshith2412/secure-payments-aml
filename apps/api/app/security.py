import base64
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from .settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd_context.verify(p, h)

def _derive_fernet_key(master: str) -> bytes:
    # Derive a fixed-length key from master secret (store master in a secret manager in real prod)
    digest = hashlib.sha256(master.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)

_f = Fernet(_derive_fernet_key(settings.encryption_master_key))

def encrypt_text(s: str) -> str:
    return _f.encrypt(s.encode("utf-8")).decode("utf-8")

def decrypt_text(token: str) -> str:
    return _f.decrypt(token.encode("utf-8")).decode("utf-8")

def create_access_token(sub: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "iss": settings.jwt_issuer,
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)
