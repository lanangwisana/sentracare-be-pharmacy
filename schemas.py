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

class ObatResponse(BaseModel):
    id: int
    name: str
    sku: str
    stock: int
    price: float
    
    class Config:
        from_attributes = True

# --- Prescription Schemas ---
class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_name: str
    obat_id: int   # <-- Berubah jadi obat_id
    quantity: int
    notes: Optional[str] = None

class PrescriptionResponse(BaseModel):
    id: int
    status: str
    obat_id: int   # <-- Berubah jadi obat_id
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True