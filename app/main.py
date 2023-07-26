from fastapi import Cookie, FastAPI, Form, Response, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import json
from jose import jwt

from .flowers_repository import FlowersRepository, FlowerRequest, FlowerResponse
# from .purchases_repository import Purchase, PurchasesRepository, SavePurchase
from .users_repository import UsersRepository, UserRequest, UserResponse

from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

flowers_repository = FlowersRepository()
# purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

def encode_jwt(user_email: str):
    data = {"user_email": user_email}
    token = jwt.encode(data, "Kamila", algorithm="HS256")
    return token

def decode_jwt(token):
    data = jwt.decode(token, "Kamila", algorithms="HS256")
    return data["user_email"]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def post_signup(user: UserRequest, db: Session=Depends(get_db)):
    users_repository.save(db, user)
    return Response()

# @app.get("/signup")
# def get_signup():
#     return users_repository

@app.post("/login")
def post_login(username: str=Form(), password: str=Form(), db: Session=Depends(get_db)):
    user = users_repository.get_user_by_email(db, username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = encode_jwt(user.email)
    return {"access_token": token, "type": "bearer"}
    
@app.get("/profile", response_model=UserResponse)
def get_profile(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    user_email = decode_jwt(token)
    user = users_repository.get_user_by_email(db, user_email)
    if not users_repository.get_user_by_email(db, user_email):
        raise HTTPException(status_code=404, detail="Not Found")
    return user

@app.get("/flowers")
def get_flowers(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db),
                skip: int=0, limit: int=10):
    flowers = flowers_repository.get_all_pagination(db, skip, limit)
    return flowers

@app.post("/flowers", response_model=FlowerResponse)
def post_flowers(flower: FlowerRequest, db: Session=Depends(get_db), token: str=Depends(oauth2_scheme)):
    return flowers_repository.save(db, flower)

@app.patch("/flowers/{flower_id}", response_model=FlowerResponse)
def patch_flower(flower_id: int, updated_flower: FlowerRequest, 
                 token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    flower = flowers_repository.update(db, updated_flower, flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")
    return flower

@app.delete("/flowers/{flower_id}")
def delete_flower(flower_id: int, token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    is_deleted = flowers_repository.delete(db, flower_id)

    if not is_deleted:
        raise HTTPException(status_code=404, detail="Flower not found")

    return {"message": "Flower deleted successfully"}

@app.post("/cart/items")
def post_cart_items(
    db: Session=Depends(get_db),
    flower_id: int=Form(), 
    cart: str=Cookie(default="[]"), 
    token: str=Depends(oauth2_scheme)):
    response = Response()
    cart_json = json.loads(cart)
    if 0 < flower_id and flower_id <= len(flowers_repository.get_all(db)):
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)
        response.set_cookie("cart", new_cart)
    return response

@app.get("/cart/items")
def get_cart_items(db: Session=Depends(get_db),
                   cart: str=Cookie(default=None), 
                   token: str=Depends(oauth2_scheme)):
    response = []
    if cart == None:
        return Response("Cart is empty", media_type="text/plain")
    cart_json = json.loads(cart)
    flowers = flowers_repository.get_list_flowers(db, cart_json)
    total_cost = 0
    for flower in flowers:
        total_cost += flower.cost
        response.append(FlowerResponse(id=flower.id, name=flower.name, cost=flower.cost))
    response.append({"total_cost": total_cost})
    return response

# @app.post("/purchased")
# def post_purchased(cart: str=Cookie(default=None), token: str=Depends(oauth2_scheme),
#                    db: Session=Depends(get_db)):
#     user_email = decode_jwt(token)
#     user = users_repository.get_user_by_email(db, user_email)
#     if not user:
#         raise HTTPException(status_code=404, detail="Not found")
#     cart_json = json.loads(cart)
#     for id in cart_json:
#         purchase = SavePurchase(user.id, id)
#         purchases_repository.save(db, purchase)

#     response = Response()
#     response.delete_cookie("cart")
#     return response

# @app.get("/purchased")
# def get_purchased(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
#     user_email = decode_jwt(token)
#     user = users_repository.get_user_by_email(db, user_email)
#     purchases = purchases_repository.get_by_user_id(db, user.id)
#     flowers = flowers_repository.get_list_flowers(db, purchases)
#     response = []
#     for flower in flowers:
#         response.append({"name": flower.name, "cost": flower.cost})
#     return response


