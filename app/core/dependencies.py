from fastapi import Header, Depends
from app.core.security import decode_token
from app.core.exceptions import InvalidTokenError, InsufficientRoleError


async def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise InvalidTokenError("Missing or malformed Authorization header")

    token = authorization.replace("Bearer ", "", 1)
    payload = decode_token(token, expected_purpose="access")

    return {
        "user_id": payload["sub"],
        "role": payload["role"],
    }


def require_role(*allowed_roles: str):
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise InsufficientRoleError()
        return current_user
    return role_checker