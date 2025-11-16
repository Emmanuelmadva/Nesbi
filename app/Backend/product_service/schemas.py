from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductResponse(ProductBase):
    id: int
    shop_id: int

    class Config:
        orm_mode = True
