from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError

from app.Backend.auth_service.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------
# Hashing des mots de passe
# ---------------------
MAX_BCRYPT_PASSWORD_LENGTH = 72  # Limite de bcrypt

def get_password_hash(password: str) -> str:
    """
    Hash le mot de passe avec bcrypt, tronqué à 72 caractères.
    """
    if len(password) > MAX_BCRYPT_PASSWORD_LENGTH:
        password = password[:MAX_BCRYPT_PASSWORD_LENGTH]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie que le mot de passe en clair correspond au hash.
    Tronque également le mot de passe à 72 caractères.
    """
    if len(plain_password) > MAX_BCRYPT_PASSWORD_LENGTH:
        plain_password = plain_password[:MAX_BCRYPT_PASSWORD_LENGTH]
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------
# Gestion des JWT
# ---------------------
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except PyJWTError:
        return None
