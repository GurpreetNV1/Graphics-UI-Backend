import httpx
from app.config import settings
from app.core.exceptions import SheetsServiceError

async def call_weekly_script(action: str, payload: dict) -> dict | list | None:
    body = {
        "secret": settings.weekly_apps_script_secret,
        "action": action,
        "payload": payload,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(settings.weekly_apps_script_url, json=body)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                raise SheetsServiceError(
                    f"Weekly Apps Script returned non-JSON. Status: {response.status_code}, Body: {response.text[:500]}"
                )
    except httpx.HTTPError as e:
        raise SheetsServiceError(f"Weekly Apps Script call failed: {str(e)}")


async def create_weekly_post(payload: dict) -> dict:
    return await call_weekly_script("createWeeklyPost", payload)

async def list_weekly_posts() -> list[dict]:
    return await call_weekly_script("listWeeklyPosts", {})

async def mark_weekly_post_done(post_id: str, feedback: str) -> dict:
    return await call_weekly_script("markWeeklyPostDone", {"post_id": post_id, "feedback": feedback})

async def add_weekly_post_review(post_id: str, note: str) -> dict:
    return await call_weekly_script("addWeeklyPostReview", {"post_id": post_id, "note": note})

async def delete_weekly_post(post_id: str) -> dict:
    return await call_weekly_script("deleteWeeklyPost", {"post_id": post_id})