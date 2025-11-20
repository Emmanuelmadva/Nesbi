from pydantic import BaseModel
from typing import Optional

class ProductResponse(BaseModel):
    id: int
    shop_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None  # <-- ajouter ici
    image_filename: Optional[str] = None

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None  # <-- ajouter ici
