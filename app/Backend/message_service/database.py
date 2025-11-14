from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Remplace par tes informations de connexion PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123@localhost:5432/nesbi"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dépendance FastAPI pour récupérer la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
