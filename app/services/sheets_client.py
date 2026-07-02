import httpx
from app.config import settings
from app.core.exceptions import SheetsServiceError

async def call_apps_script(action: str, payload: dict) -> dict | None:
    body = {
        "secret": settings.apps_script_secret,
        "action": action,
        "payload": payload,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(settings.apps_script_url, json=body)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise SheetsServiceError(f"Apps Script call failed: {str(e)}")

# ===== Wrapper functions matching Code.gs actions =====
async def get_user_by_email(email: str) -> dict | None:
    return await call_apps_script("getUserByEmail", {"email": email})


async def get_user_by_id(user_id: str) -> dict | None:
    return await call_apps_script("getUserById", {"user_id": user_id})


async def update_password(user_id: str, new_hash: str) -> dict:
    return await call_apps_script("updatePassword", {"user_id": user_id, "new_hash": new_hash})


async def update_refresh_token(user_id: str, token_hash: str) -> dict:
    return await call_apps_script("updateRefreshToken", {"user_id": user_id, "hash": token_hash})


async def clear_refresh_token(user_id: str) -> dict:
    return await call_apps_script("clearRefreshToken", {"user_id": user_id})


async def update_last_login(user_id: str, timestamp: str) -> dict:
    return await call_apps_script("updateLastLogin", {"user_id": user_id, "timestamp": timestamp})


async def set_otp(user_id: str, otp_hash: str, expires_at: str) -> dict:
    return await call_apps_script("setOtp", {"user_id": user_id, "otp_hash": otp_hash, "expires_at": expires_at})


async def clear_otp(user_id: str) -> dict:
    return await call_apps_script("clearOtp", {"user_id": user_id})


async def send_otp_email(email: str, otp: str) -> dict:
    return await call_apps_script("sendOtpEmail", {"email": email, "otp": otp})