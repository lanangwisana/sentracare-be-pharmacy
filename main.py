from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, cast

from database import Base, engine, SessionLocal
from models import Obat, Prescription
from schemas import ObatCreate, ObatResponse, PrescriptionCreate, PrescriptionResponse

app = FastAPI(title="Sentracare Pharmacy Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- OBAT ENDPOINTS ---

@app.post("/pharmacy/obat", response_model=ObatResponse, tags=["obat"])
def create_obat(data: ObatCreate, db: Session = Depends(get_db)):
    existing: Optional[Obat] = db.query(Obat).filter(Obat.sku == data.sku).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Kode SKU obat sudah ada")
    
    new_obat = Obat(**data.dict())
    db.add(new_obat)
    db.commit()
    db.refresh(new_obat)
    return new_obat

@app.get("/pharmacy/obat", response_model=List[ObatResponse], tags=["obat"])
def get_obat_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Obat).offset(skip).limit(limit).all()

@app.get("/pharmacy/obat/{obat_id}", response_model=ObatResponse, tags=["obat"])
def get_obat_detail(obat_id: int, db: Session = Depends(get_db)):
    item: Optional[Obat] = db.query(Obat).filter(Obat.id == obat_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
    return item

# --- PRESCRIPTION ENDPOINTS ---

@app.post("/pharmacy/prescriptions", response_model=PrescriptionResponse, tags=["prescriptions"])
def create_prescription(data: PrescriptionCreate, db: Session = Depends(get_db)):
    item: Optional[Obat] = db.query(Obat).filter(Obat.id == data.obat_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
    
    stock_value = cast(int, item.stock)
    if stock_value < data.quantity:
        raise HTTPException(status_code=400, detail=f"Stok tidak cukup. Sisa: {stock_value}")

    # Kurangi stok
    item.stock = stock_value - data.quantity # type: ignore
    
    new_prescription = Prescription(
        patient_id=data.patient_id,
        doctor_name=data.doctor_name,
        obat_id=data.obat_id,
        quantity=data.quantity,
        notes=data.notes,
        status="PROCESSED"
    )
    
    db.add(new_prescription)
    db.add(item)
    db.commit()
    db.refresh(new_prescription)
    
    return new_prescription