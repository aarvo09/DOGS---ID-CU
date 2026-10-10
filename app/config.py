import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Application Configuration
APP_NAME = "Chandigarh University - Campus Dog Digital Identity System"
APP_VERSION = "1.0.0"
BASE_URL = os.getenv("BASE_URL", os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000"))

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "dogcu.db"))

# Security Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "cu-dog-digital-identity-super-secret-key-2026-chandigarh-university")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours

# Upload Configuration
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

# Rate Limiting Configuration (Per IP per minute)
RATE_LIMIT_SIGHTINGS_PER_MINUTE = int(os.getenv("RATE_LIMIT_SIGHTINGS_PER_MINUTE", "15"))
RATE_LIMIT_REPORTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REPORTS_PER_MINUTE", "10"))
