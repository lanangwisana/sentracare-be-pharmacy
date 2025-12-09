from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Obat(Base):
    __tablename__ = "obat"  # <-- Nama tabel berubah jadi 'obat'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_name = Column(String(100), nullable=False)
    
    # Ubah relasi ke tabel obat
    obat_id = Column(Integer, ForeignKey("obat.id"), nullable=False) 
    quantity = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    obat = relationship("Obat")