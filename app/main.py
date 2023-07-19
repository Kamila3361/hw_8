from fastapi import Cookie, FastAPI, Form, Request, Response, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import json

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
from jose import jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

def encode_jwt(user_email: str):
    data = {"user_email": user_email}
    token = jwt.encode(data, "Kamila", algorithm="HS256")
    return token

def hash_jwt(password: str):
    data = {"password": password}
    hashed_password = jwt.encode(data, "Kamila", algorithm="HS256")
    return hashed_password

def decode_jwt(token):
    data = jwt.decode(token, "Kamila", algorithms="HS256")
    return data


@app.post("/signup")
def post_signup(email: str=Form(),
    full_name: str=Form(),
    password: str=Form()):
    hashed_password = hash_jwt(password)
    user = User(email=email, full_name=full_name, hashed_password=hashed_password)
    users_repository.save(user)
    return Response()

@app.get("/signup")
def get_signup():
    return users_repository

@app.post("/login")
def post_login(username: str=Form(), password: str=Form()):
    user = users_repository.get_by_email(username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    hashed_password = hash_jwt(password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = encode_jwt(user.email)
    return {"access_token": token, "type": "bearer"}
    
@app.get("/profile")
def get_profile(token: str=Depends(oauth2_scheme)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(user_email["user_email"])
    if not users_repository.get_by_email(user_email["user_email"]):
        raise HTTPException(status_code=404, detail="Not Found")
    return {"email": user.email, "full_name": user.full_name, "id": user.id}

@app.get("/flowers")
def get_flowers(token: str=Depends(oauth2_scheme)):
    flowers = flowers_repository.get_all()
    return flowers

@app.post("/flowers")
def post_flowers(flower: Flower, token: str=Depends(oauth2_scheme)):
    id = flowers_repository.save(flower)
    return {"flower_id": id}

@app.post("/cart/items")
def post_cart_items(
    flower_id: int=Form(), 
    cart: str=Cookie(default="[]"), 
    token: str=Depends(oauth2_scheme)):
    response = Response()
    cart_json = json.loads(cart)
    if 0 < flower_id and flower_id <= len(flowers_repository.get_all()):
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)
        response.set_cookie("cart", new_cart)
    return response

@app.get("/cart/items")
def get_cart_items(cart: str=Cookie(default=None), token: str=Depends(oauth2_scheme)):
    response = []
    if cart == None:
        return Response("Cart is empty", media_type="text/plain")
    cart_json = json.loads(cart)
    flowers = flowers_repository.get_list_flowers(cart_json)
    total_cost = 0
    for flower in flowers:
        total_cost += flower.cost
        response.append({"flower_id": flower.id, "name": flower.name, "cost": flower.cost})
    response.append({"total_cost": total_cost})
    return response

@app.post("/purchased")
def post_purchased(cart: str=Cookie(default=None), token: str=Depends(oauth2_scheme)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(user_email["user_email"])
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    cart_json = json.loads(cart)
    for id in cart_json:
        purchase = Purchase(user.id, id)
        purchases_repository.save(purchase)

    response = Response()
    response.delete_cookie("cart")
    return response

@app.get("/purchased")
def get_purchased(token: str=Depends(oauth2_scheme)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(user_email["user_email"])
    purchases = purchases_repository.get_by_user_id(user.id)
    flowers = flowers_repository.get_list_flowers(purchases)
    response = []
    for flower in flowers:
        response.append({"name": flower.name, "cost": flower.cost})
    return response


