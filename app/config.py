from dotenv import load_dotenv
import os

load_dotenv()

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

# DATABASE_URL = os.getenv("DATABASE_URL")
# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# GOOGLE_REFRESH_TOKEN  = os.getenv("GOOGLE_REFRESH_TOKEN")