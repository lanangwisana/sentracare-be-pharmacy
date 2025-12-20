from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Obat Schemas ---
class ObatCreate(BaseModel):
    name: str
    sku: str
    stock: int
    price: float
    description: Optional[str] = None
    category: Optional[str] = None

class ObatResponse(BaseModel):
    id: int
    name: str
    sku: str
    stock: int
    price: float
    description: Optional[str] = None
    category: Optional[str] = None 
    class Config:
        from_attributes = True