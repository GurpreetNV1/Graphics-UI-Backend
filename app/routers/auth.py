from fastapi import APIRouter, Header, Depends
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
)
from app.schemas.response import SuccessResponse
from app.core.exceptions import MustResetPasswordError, UserNotFoundError
from app.core.security import decode_token
from app.services import auth_service
from app.services import sheets_client
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=SuccessResponse)
async def login(payload: LoginRequest):
    try:
        result = await auth_service.login(payload.email, payload.password)
        return SuccessResponse(message="Login successful", data=result)
    except MustResetPasswordError as e:
        # Not a real error — a valid flow branch, so we still return 200
        return SuccessResponse(
            message="Password reset required",
            data={"action": "must_reset_password", "reset_token": e.reset_token},
        )

@router.post("/refresh", response_model=SuccessResponse)
async def refresh(payload: RefreshRequest):
    result = await auth_service.refresh_access_token(payload.refresh_token)
    return SuccessResponse(message="Token refreshed", data=result)

@router.post("/logout", response_model=SuccessResponse)
async def logout(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token, expected_purpose="access")
    await auth_service.logout(payload["sub"])
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
async def reset_password(payload: ResetPasswordRequest):
    result = await auth_service.reset_password(payload.reset_token, payload.new_password)
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