import strawberry
from typing import List, Optional
from models import Obat
from database import SessionLocal

@strawberry.type
class ObatType:
    id: int
    name: str
    sku: str
    stock: int
    price: float
    description: Optional[str]
    category: Optional[str]

    @staticmethod
    def from_model(model: Obat) -> "ObatType":
        return ObatType(
            id=model.id, # type: ignore
            name=model.name, # type: ignore
            sku=model.sku, # type: ignore   
            stock=model.stock, # type: ignore
            price=model.price, # type: ignore
            description=model.description or "", # type: ignore
            category=model.category or "" # type: ignore
        )

@strawberry.type
class Query:
    @strawberry.field(name="obat_list")
    def get_obat_list(self) -> List[ObatType]:
        db = SessionLocal()
        try:
            records = db.query(Obat).all()
            return [ObatType.from_model(b) for b in records]
        finally:
            db.close()

schema = strawberry.Schema(query=Query)