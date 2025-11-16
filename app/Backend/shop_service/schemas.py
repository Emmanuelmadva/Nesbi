from pydantic import BaseModel, Field
from typing import Optional

class ShopBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ShopCreate(ShopBase):
    pass

class ShopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ShopResponse(ShopBase):
    id: int
    owner_id: int
    is_active: bool
    logo_filename: Optional[str] = None

    class Config:
        from_attributes = True
