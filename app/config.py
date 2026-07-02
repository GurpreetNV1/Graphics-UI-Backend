from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 15

    # Apps Script
    apps_script_url: str
    apps_script_secret: str

    # OTP
    otp_expire_minutes: int = 10
    otp_length: int = 6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()