from attrs import define
from pydantic import BaseModel

class User(BaseModel):
    email: str
    full_name: str
    hashed_password: str
    id: int = 0


class UsersRepository:
    users: list[User]

    def __init__(self):
        self.users = []

    def save(self, user: User):
        user.id = len(self.users) + 1
        self.users.append(user)
        return user
    
    def get_by_email(self, email: str):
        for user in self.users:
            if email == user.email:
                return user
        return None
    
