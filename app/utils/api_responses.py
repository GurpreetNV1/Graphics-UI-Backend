from typing import Any, Optional, List, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import traceback

class APIResponse(BaseModel):
    status_code: int = 200
    data: Optional[Any] = []
    message: str = "Success"
    success: bool = True

    def to_response(self, cookies: Optional[List[Dict[str, Any]]] = None) -> JSONResponse:
        resp = JSONResponse(
            status_code=self.status_code,
            content=jsonable_encoder({
                "success": self.success,
                "message": self.message,
                "data": self.data,
                "status_code": self.status_code,
            }),
            
        )

        if cookies:
            for c in cookies:
                key = c.get("key")
                value = c.get("value")
                if not key:
                    continue

                # --- Validate SameSite properly ---
                samesite = c.get("samesite", "lax")
                if isinstance(samesite, str):
                    samesite = samesite.lower()

                valid_samesite = {"lax", "strict", "none"}
                if samesite not in valid_samesite:
                    samesite = "lax"

                # --- Enforce Chrome rules ---
                # If SameSite=None → Secure MUST be True
                secure = c.get("secure", True)
                if samesite == "none":
                    secure = True

                # --- Set cookie ---
                resp.set_cookie(
                    key=key,
                    value=value,
                    max_age=c.get("max_age"),
                    expires=c.get("expires"),
                    path=c.get("path", "/"),
                    domain=c.get("domain"),
                    httponly=c.get("httponly", True),
                    secure=secure,
                    samesite=samesite,
                )


        return resp

class APIError(Exception):
    def __init__(
        self,
        status_code: int = 500,
        message: str = "Something went wrong",
        errors: Optional[List[Any]] = None,
        # stack: Optional[str] = None,
        stack: str | None = None,
        data = Any
    ):
        self.status_code = status_code
        self.success = False
        self.data = None
        self.message = message
        self.errors = errors or []
        # self.stack = stack
        self.stack = stack or traceback.format_exc()
        super().__init__(message)

    def to_response(self):
        print("=" * 50)
        print("API ERROR")
        print(f"Status Code: {self.status_code}")
        print(f"Message: {self.message}")
        print(f"Errors: {self.errors}")
        if self.stack:
            print("TRACEBACK:")
            print(self.stack)
        print("=" * 50)

        return JSONResponse(
            status_code=self.status_code,
            content={
                "success": False,
                "message": self.message,
                "data": None,
                "errors":self.errors
            },
        )