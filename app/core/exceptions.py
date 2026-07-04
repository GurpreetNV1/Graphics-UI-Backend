class AppException(Exception):
    """Base exception for all custom app errors."""
    def __init__(self, message: str, status_code: int = 400, error_code: str | None = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__("Invalid email or password", status_code=401, error_code="INVALID_CREDENTIALS")


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__("User not found", status_code=404, error_code="USER_NOT_FOUND")


class AccountDisabledError(AppException):
    def __init__(self):
        super().__init__("Account is disabled", status_code=403, error_code="ACCOUNT_DISABLED")


class MustResetPasswordError(AppException):
    def __init__(self, reset_token: str):
        self.reset_token = reset_token
        super().__init__("Password reset required", status_code=200, error_code="MUST_RESET_PASSWORD")


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, status_code=401, error_code="INVALID_TOKEN")


class InvalidOtpError(AppException):
    def __init__(self):
        super().__init__("Invalid or expired OTP", status_code=400, error_code="INVALID_OTP")


class SheetsServiceError(AppException):
    def __init__(self, message: str = "Failed to communicate with data layer"):
        super().__init__(message, status_code=502, error_code="SHEETS_SERVICE_ERROR")

class InsufficientRoleError(AppException):
    def __init__(self):
        super().__init__("You do not have permission to perform this action", status_code=403, error_code="FORBIDDEN")

class RequestNotFoundError(AppException):
    def __init__(self):
        super().__init__("Request not found", status_code=404, error_code="REQUEST_NOT_FOUND")

class InvalidStatusTransitionError(AppException):
    def __init__(self, message: str = "This action isn't allowed for the request's current status"):
        super().__init__(message, status_code=400, error_code="INVALID_STATUS_TRANSITION")