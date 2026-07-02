import random
import string
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.core.security import (
    hash_value,
    verify_value,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
)
from app.core.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    AccountDisabledError,
    MustResetPasswordError,
    InvalidOtpError,
    InvalidTokenError,
)
from app.services import sheets_client


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_truthy(value) -> bool:
    """Apps Script may return actual booleans or string 'TRUE'/'FALSE' — normalize."""
    if isinstance(value, bool):
        return value
    return str(value).strip().upper() == "TRUE"


async def login(email: str, password: str) -> dict:
    user = await sheets_client.get_user_by_email(email)
    if not user:
        raise InvalidCredentialsError()  # don't leak "user not found" vs "wrong password"

    if not _is_truthy(user.get("is_active")):
        raise AccountDisabledError()

    if not verify_value(password, user.get("password_hash", "")):
        raise InvalidCredentialsError()

    user_id = user["user_id"]

    if _is_truthy(user.get("must_reset_password")):
        reset_token = create_reset_token(user_id)
        raise MustResetPasswordError(reset_token=reset_token)

    access_token = create_access_token(user_id, user["role"])
    refresh_token = create_refresh_token(user_id)

    await sheets_client.update_refresh_token(user_id, hash_value(refresh_token))
    await sheets_client.update_last_login(user_id, _now_iso())

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user.get("name"),
    }


async def refresh_access_token(refresh_token: str) -> dict:
    payload = decode_token(refresh_token, expected_purpose="refresh")
    user_id = payload["sub"]

    user = await sheets_client.get_user_by_id(user_id)
    if not user:
        raise UserNotFoundError()

    if not _is_truthy(user.get("is_active")):
        raise AccountDisabledError()

    if not verify_value(refresh_token, user.get("refresh_token_hash", "")):
        raise InvalidTokenError("Refresh token no longer valid, please log in again")

    new_access_token = create_access_token(user_id, user["role"])

    return {"access_token": new_access_token, "token_type": "bearer"}


async def logout(user_id: str) -> None:
    await sheets_client.clear_refresh_token(user_id)


async def reset_password(reset_token: str, new_password: str) -> dict:
    payload = decode_token(reset_token, expected_purpose="reset")
    user_id = payload["sub"]

    user = await sheets_client.get_user_by_id(user_id)
    if not user:
        raise UserNotFoundError()

    new_hash = hash_value(new_password)
    await sheets_client.update_password(user_id, new_hash)
    await sheets_client.clear_otp(user_id)  # in case this came via forgot-password/OTP flow

    # Log them in immediately after reset, same as a normal login
    access_token = create_access_token(user_id, user["role"])
    refresh_token = create_refresh_token(user_id)
    await sheets_client.update_refresh_token(user_id, hash_value(refresh_token))
    await sheets_client.update_last_login(user_id, _now_iso())

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user.get("name"),
    }


async def forgot_password(email: str) -> None:
    user = await sheets_client.get_user_by_email(email)
    if not user:
        # Don't reveal whether the email exists — silently succeed either way
        return

    if not _is_truthy(user.get("is_active")):
        return

    otp = "".join(random.choices(string.digits, k=settings.otp_length))
    otp_hash = hash_value(otp)
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)).isoformat()

    await sheets_client.set_otp(user["user_id"], otp_hash, expires_at)
    await sheets_client.send_otp_email(email, otp)


async def verify_otp(email: str, otp: str) -> str:
    user = await sheets_client.get_user_by_email(email)
    if not user:
        raise InvalidOtpError()

    stored_hash = user.get("otp", "")
    expires_at = user.get("otp_expires_at", "")

    if not stored_hash or not expires_at:
        raise InvalidOtpError()

    expiry_dt = datetime.fromisoformat(expires_at)
    if datetime.now(timezone.utc) > expiry_dt:
        raise InvalidOtpError()

    if not verify_value(otp, stored_hash):
        raise InvalidOtpError()

    return create_reset_token(user["user_id"])