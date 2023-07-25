from attrs import define
from pydantic import BaseModel

from .database import Base
from sqlalchemy import String, Integer, ForeignKey, Column
from sqlalchemy.orm import Session, relationship

class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    cost = Column(Integer)
    count = Column(Integer)

    # purchase = relationship("Purchase", back_populates="flower")

class FlowerRequest(BaseModel):
    name: str
    cost: int
    count: int

class FlowerResponse(BaseModel):
    id: int
    name: str
    cost: int

@define
class SaveFlower():
    name: str
    cost: int
    count: int

class FlowersRepository:
    def get_all(self, db: Session) -> list[Flower]:
        return db.query(Flower).all()

    def get_all_pagination(self, db: Session, skip: int, limit: int) -> list[Flower]:
        return db.query(Flower).offset(skip).limit(limit).all()
    
    def get_list_flowers(self, db: Session, ids: list) -> list[Flower]:
        flowers = []
        for id in ids:
            flowers.append(db.query(Flower).filter(Flower.id == id).first())
        return flowers

    def save(self, db: Session, flower: SaveFlower) -> Flower:
        db_flower = Flower(name=flower.name, cost=flower.cost, count=flower.count)
        db.add(db_flower)
        db.commit()
        db.refresh(db_flower)
        return db_flower
    
    def update(self, db: Session, updated_flower: SaveFlower, flower_id: int) -> Flower:
        flower = db.query(Flower).filter(Flower.id == flower_id).first()
        if flower:
            flower.name = updated_flower.name
            flower.cost = updated_flower.cost
            flower.count = updated_flower.count
        db.commit()
        db.refresh(flower)
        return flower
        
    def delete(self, db: Session, flower_id: int):
        flower = db.query(Flower).filter(Flower.id == flower_id).first()
        if flower:
            db.delete(flower)
            db.commit()
            return True
        else:
            return False