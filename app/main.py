from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse
import json

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
from jose import jwt

app = FastAPI()
templates = templating.Jinja2Templates("templates")


flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

def encode_jwt(user_email: str):
    data = {"user_email": user_email}
    token = jwt.encode(data, "Kamila", algorithm="HS256")
    return token

def decode_jwt(token):
    data = jwt.decode(token, "Kamila", algorithms="HS256")
    return data

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup")
def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {
        "request": request
    })

@app.post("/signup")
def post_signup(
    email: str=Form(),
    full_name: str=Form(),
    password: str=Form()):
    user = User(email, full_name, password)
    users_repository.save(user)
    return RedirectResponse("/login", status_code=303)

@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@app.post("/login")
def post_login(email: str=Form(), password: str=Form()):
    if users_repository.get_by_email(email) == None:
        return Response("Not found", status_code=404)
    else:
        user = users_repository.get_by_email(email)

    if password != user.password:
        return Response("Not found", status_code=404)
    
    response = RedirectResponse("/profile", status_code=303)
    token = encode_jwt(user.email)
    response.set_cookie("token", token)

    return response
    
@app.get("/profile")
def get_profile(request: Request ,token: str=Cookie(default=None)):
    user_email = decode_jwt(token)
    if users_repository.get_by_email(user_email["user_email"]) == None:
        return Response("Not found", status_code=404)
    else:
        user = users_repository.get_by_email(user_email["user_email"])
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@app.get("/flowers")
def get_flowers(request: Request):
    flowers = flowers_repository.get_all()
    return templates.TemplateResponse("flowers_page.html", {
        "request": request,
        "flowers": flowers
    })

@app.post("/flowers")
def post_flowers(name: str=Form(), count: int=Form(), cost: int=Form()):
    flower = Flower(name, count, cost)
    flowers_repository.save(flower)
    return RedirectResponse("/flowers", status_code=303)

@app.post("/cart/items")
def post_cart_items(flower_id: int=Form(), cart: str=Cookie(default="[]")):
    response = RedirectResponse("/flowers", status_code=303)
    cart_json = json.loads(cart)
    if 0 < flower_id and flower_id <= len(flowers_repository.get_all()):
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)
        response.set_cookie("cart", new_cart)
    return response

@app.get("/cart/items")
def get_cart_items(request: Request, cart: str=Cookie(default=None)):
    if cart == None:
        return Response("Cart is empty", media_type="text/plain")
    cart_json = json.loads(cart)
    flowers = flowers_repository.get_list_flowers(cart_json)
    all_cost = 0
    for flower in flowers:
        all_cost += flower.cost
    return templates.TemplateResponse("cart_items.html", {
        "request": request,
        "flowers": flowers, 
        "all_cost": all_cost
    })

@app.post("/purchased")
def post_purchased(cart: str=Cookie(default=None), token: str=Cookie(default=None)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(user_email["user_email"])
    cart_json = json.loads(cart)
    for id in cart_json:
        purchase = Purchase(user.id, id)
        purchases_repository.save(purchase)

    response = RedirectResponse("/purchased", status_code=303)
    response.delete_cookie("cart")
    return response

@app.get("/purchased")
def get_purchased(request: Request, token: str=Cookie(default=None)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(user_email["user_email"])
    purchases = purchases_repository.get_by_user_id(user.id)
    flowers = flowers_repository.get_list_flowers(purchases)

    return templates.TemplateResponse("purchase.html", {
        "request": request,
        "flowers": flowers
    })
    


