import strawberry
from typing import List
from models import Obat
from database import SessionLocal

@strawberry.type
class ObatType:
    id: int
    name: str
    stock: str
    description: str

    @staticmethod
    def from_model(model: Obat) -> "ObatType":
        return ObatType(
            id=model.id, # type: ignore
            name=model.name, # type: ignore
            stock=model.stock, # type: ignore
            description=model.description  # type: ignore
        )

@strawberry.type
class Query:
    @strawberry.field
    def obats(self) -> List[ObatType]:
        db = SessionLocal()
        try:
            records = db.query(Obat).all()
            return [ObatType.from_model(b) for b in records]
        finally:
            db.close()

schema = strawberry.Schema(query=Query)