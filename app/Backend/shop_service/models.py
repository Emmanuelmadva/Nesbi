from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
from database import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False, index=True)  # ID venant de auth-service
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)

    # Stockage du logo directement dans la DB
    logo = Column(LargeBinary, nullable=True)
    logo_filename = Column(String(255), nullable=True)  # pour conserver le nom original
    logo_content_type = Column(String(50), nullable=True)  # type MIME

    is_active = Column(Boolean, default=True, nullable=False)
