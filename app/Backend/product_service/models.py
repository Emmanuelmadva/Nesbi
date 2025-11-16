from sqlalchemy import Column, Integer, String, Float, ForeignKey, LargeBinary, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(150), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # Image
    image = Column(LargeBinary, nullable=True)
    image_filename = Column(String(255), nullable=True)
    image_content_type = Column(String(100), nullable=True)

    # Date de création
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shop = relationship("Shop")
