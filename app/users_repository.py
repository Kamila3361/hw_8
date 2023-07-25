from attrs import define
from pydantic import BaseModel

from sqlalchemy import Boolean, Column, Integer, ForeignKey, String
from sqlalchemy.orm import Session, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    surname = Column(String)
    password = Column(String)

    # purchase = relationship("Purchase", back_populates="user")

class UserRequest(BaseModel):
    email: str
    name: str
    surname: str
    password: str

class UserResponse(BaseModel):
    email: str
    name: str
    surname: str

@define
class SaveUser():
    email: str
    name: str
    surname: str
    password: str

class UsersRepository:
    def get_user(self, db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, user_email: str) -> User:
        return db.query(User).filter(User.email == user_email).first()
    
    def save(self, db: Session, user: SaveUser) -> User:
        db_user = User(email=user.email, name=user.name, 
                       surname=user.surname, password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
