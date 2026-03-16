import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.APP_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def verify_github_signature(payload_body: bytes, signature: str) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature.

    Uses hmac.digest() — the correct, C-accelerated one-shot API in Python 3.7+.
    hmac.compare_digest() prevents timing side-channel attacks.
    """
    if not signature or not signature.startswith("sha256="):
        return False
    secret = getattr(settings, "GITHUB_WEBHOOK_SECRET", None)
    if not secret:
        return False
    expected_bytes = hmac.digest(
        secret.encode("utf-8"),
        payload_body,
        "sha256",
    )
    expected_sig = "sha256=" + expected_bytes.hex()
    return hmac.compare_digest(expected_sig, signature)
