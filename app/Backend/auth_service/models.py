from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum

class UserRole(enum.Enum):
    admin = "admin"
    vendeur = "vendeur"
    acheteur = "acheteur"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.acheteur)
