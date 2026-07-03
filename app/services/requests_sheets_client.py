import httpx
from app.config import settings
from app.core.exceptions import SheetsServiceError

async def call_requests_script(action: str, payload: dict) -> dict | list | None:
    body = {
        "secret": settings.requests_apps_script_secret,
        "action": action,
        "payload": payload,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(settings.requests_apps_script_url, json=body)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                raise SheetsServiceError(
                    f"Requests Apps Script returned non-JSON. Status: {response.status_code}, Body: {response.text[:500]}"
                )
    except httpx.HTTPError as e:
        raise SheetsServiceError(f"Requests Apps Script call failed: {str(e)}")


# ===== Wrapper functions matching Code.gs actions =====
async def create_request(payload: dict) -> dict:
    return await call_requests_script("createRequest", payload)


async def get_request_by_id(request_id: str) -> dict | None:
    return await call_requests_script("getRequestById", {"request_id": request_id})


async def list_requests() -> list[dict]:
    return await call_requests_script("listRequests", {})


async def update_request(request_id: str, fields: dict) -> dict:
    return await call_requests_script("updateRequest", {"request_id": request_id, "fields": fields})


async def add_comment(payload: dict) -> dict:
    return await call_requests_script("addComment", payload)


async def get_comments_by_request_id(request_id: str) -> list[dict]:
    return await call_requests_script("getCommentsByRequestId", {"request_id": request_id})