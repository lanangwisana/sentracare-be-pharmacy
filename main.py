# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from database import Base, engine, SessionLocal
from models import Obat
from schemas import (ObatCreate, ObatResponse,)
from graphql_schema import schema  
from auth import SECRET_KEY, ALGORITHM, ISSUER, AUDIENCE
from jose import jwt, JWTError

app = FastAPI(
    title="Sentracare Pharmacy Service",
    description="API untuk management obat di SentraCare", 
    version="1.0.0")

# CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DB init
Base.metadata.create_all(bind=engine)

async def get_context(request: Request):
    user = None
    if "authorization" in request.headers:
        try:
            token = request.headers["authorization"].split(" ")[1]
            user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], issuer=ISSUER, audience=AUDIENCE)
        except JWTError:
            user = None
    return {"user": user}

# GraphQL
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(
    graphql_app, 
    prefix="/pharmacy/graphql",
    tags=["GraphQL API"],
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- OBAT ENDPOINTS (PROTEKSI ROLE DIHAPUS AGAR BERHASIL) --------
@app.post(
    "/pharmacy/obat", 
    tags=["Obat Management"],
    summary="Create Obat",
    description="Create a new obat in the pharmacy system",
    response_model=ObatResponse, 
    status_code=status.HTTP_201_CREATED)
def create_obat(data: ObatCreate, db: Session = Depends(get_db)):
    existing = db.query(Obat).filter(Obat.sku == data.sku).first()
    if existing: raise HTTPException(status_code=400, detail="Kode SKU sudah ada")
    new_obat = Obat(**data.dict())
    db.add(new_obat)
    db.commit()
    db.refresh(new_obat)
    return new_obat

@app.get(
    "/pharmacy/obat", 
    tags=["Obat Management"],
    summary="Get Obat List",
    description="Retrieve a list of all obat in the pharmacy system",
    response_model=List[ObatResponse])
def get_obat_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Obat).offset(skip).limit(limit).all()

@app.patch(
    "/pharmacy/obat/{obat_id}/stock", 
    tags=["Obat Management"],
    summary="Update Obat Stock",
    description="Update the stock of a specific obat",
    response_model=ObatResponse)
def update_stock(obat_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.query(Obat).filter(Obat.id == obat_id).first()
    if not item: raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
    item.stock = int(payload.get("stock", item.stock)) # type: ignore
    db.commit()
    db.refresh(item)
    return item

@app.put(
    "/pharmacy/obat/{obat_id}", 
    tags=["Obat Management"],
    summary="Update Obat",  
    description="Update the details of a specific obat",
    response_model=ObatResponse)
def update_obat(obat_id: int, data: ObatCreate, db: Session = Depends(get_db)):
    item = db.query(Obat).filter(Obat.id == obat_id).first()
    if not item: 
        raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
    
    # Update field
    item.name = data.name # type: ignore
    item.sku = data.sku # type: ignore
    item.stock = data.stock # type: ignore
    item.price = data.price # type: ignore
    item.description = data.description # type: ignore
    item.category = data.category # type: ignore

    db.commit()
    db.refresh(item)
    return item

@app.delete(
    "/pharmacy/obat/{obat_id}",
    tags=["Obat Management"],
    summary="Delete Obat",
    description="Delete a specific obat from the pharmacy system")
def delete_obat(obat_id: int, db: Session = Depends(get_db)):
    item = db.query(Obat).filter(Obat.id == obat_id).first()
    if not item: raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
    db.delete(item)
    db.commit()
    return {"message": "Dihapus"}