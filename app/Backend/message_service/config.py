import os
from dotenv import load_dotenv

load_dotenv()

# Exemple pour JWT ou autres secrets
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 jour
