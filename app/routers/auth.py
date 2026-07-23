from fastapi import APIRouter, Header, Depends, Response, Request
from app.schemas.auth import (
    LoginRequest,
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
)
from app.schemas.response import SuccessResponse
from app.core.exceptions import MustResetPasswordError, UserNotFoundError, InvalidTokenError
from app.core.security import decode_token
from app.services import auth_service
from app.services import sheets_client
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds, matches your token expiry


def _set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,      # set True once you're on HTTPS in production
        samesite="none",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/",
    )


@router.post("/login", response_model=SuccessResponse)
async def login(payload: LoginRequest, response: Response):
    try:
        result = await auth_service.login(payload.email, payload.password)
        refresh_token = result.pop("refresh_token")  # take it out of the body
        _set_refresh_cookie(response, refresh_token)
        return SuccessResponse(message="Login successful", data=result)
    except MustResetPasswordError as e:
        return SuccessResponse(
            message="Password reset required",
            data={"action": "must_reset_password", "reset_token": e.reset_token},
        )


@router.post("/refresh", response_model=SuccessResponse)
async def refresh(request: Request):
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise InvalidTokenError("No refresh token found, please log in again")

    result = await auth_service.refresh_access_token(refresh_token)
    return SuccessResponse(message="Token refreshed", data=result)


@router.post("/logout", response_model=SuccessResponse)
async def logout(response: Response, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token, expected_purpose="access")
    await auth_service.logout(payload["sub"])
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    return SuccessResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(payload: ForgotPasswordRequest):
    await auth_service.forgot_password(payload.email)
    return SuccessResponse(message="If this email exists, an OTP has been sent")


@router.post("/verify-otp", response_model=SuccessResponse)
async def verify_otp(payload: VerifyOtpRequest):
    reset_token = await auth_service.verify_otp(payload.email, payload.otp)
    return SuccessResponse(message="OTP verified", data={"reset_token": reset_token})


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(payload: ResetPasswordRequest, response: Response):
    result = await auth_service.reset_password(payload.reset_token, payload.new_password)
    refresh_token = result.pop("refresh_token")
    _set_refresh_cookie(response, refresh_token)
    return SuccessResponse(message="Password reset successful", data=result)


@router.get("/me", response_model=SuccessResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await sheets_client.get_user_by_id(current_user["user_id"])
    if not user:
        raise UserNotFoundError()

    return SuccessResponse(
        message="User fetched",
        data={
            "user_id": user["user_id"],
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
        },
    )
