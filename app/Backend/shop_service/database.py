# shop_service/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.Backend.shop_service.config import DATABASE_URL

# Créer le moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={},  # pour PostgreSQL, on peut laisser vide
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour tous les modèles
Base = declarative_base()

# Dépendance FastAPI pour récupérer la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

