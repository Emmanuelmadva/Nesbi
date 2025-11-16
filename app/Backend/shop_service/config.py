# shop_service/config.py
import os
from datetime import timedelta

# ==============================
# JWT Configuration (auth-service)
# ==============================
# Shop-service va uniquement décoder les JWT fournis par auth-service
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "supersecretkeynesbi")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

# ==============================
# Database Configuration
# ==============================
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "123")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "nesbi")

# URL SQLAlchemy compatible PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ==============================
# App Configuration
# ==============================
APP_NAME = os.environ.get("APP_NAME", "Nesbi Shop Service")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
