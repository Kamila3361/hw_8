# from attrs import define
# from pydantic import BaseModel

# from sqlalchemy.orm import Session, relationship
# from sqlalchemy import Integer, ForeignKey, Column
# from .database import Base

# class Purchase(Base):
#     __tablename__ = "purchases"
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), unique=False)
#     flower_id = Column(Integer, ForeignKey("flowers.id"), unique=False)

#     user = relationship("User", back_populates="purchase")
#     flower = relationship("Flower", back_populates="purchase")

# @define
# class SavePurchase():
#     user_id: int
#     flower_id: int

# class PurchasesRepository:
#     def save(self, db: Session, purchase: SavePurchase) -> Purchase:
#         db_purchase = Purchase(user_id=purchase.user_id, flower_id=purchase.flower_id)
#         db.add(db_purchase)
#         db.commit()
#         db.refresh(db_purchase)
#         return db_purchase
    
#     def get_by_user_id(self, db: Session, user_id) -> list[Purchase]:
#         return db.query(Purchase.flower_id).filter(Purchase.user_id == user_id).all()
