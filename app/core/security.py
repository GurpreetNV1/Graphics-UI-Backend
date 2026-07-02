from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.config import settings
from app.core.exceptions import InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== Password hashing =====
def hash_value(value: str) -> str:
    """Used for both passwords and OTPs — same one-way hashing pattern."""
    return pwd_context.hash(value)


def verify_value(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    return pwd_context.verify(plain, hashed)

# ===== JWT creation =====
def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        {"sub": user_id, "role": role, "purpose": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )

def create_refresh_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "purpose": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )

def create_reset_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "purpose": "reset"},
        timedelta(minutes=settings.reset_token_expire_minutes),
    )

# ===== JWT verification =====
def decode_token(token: str, expected_purpose: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise InvalidTokenError()

    if payload.get("purpose") != expected_purpose:
        raise InvalidTokenError(f"Token is not valid for this action")

    return payload