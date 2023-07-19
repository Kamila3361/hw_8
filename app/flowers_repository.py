from attrs import define
from pydantic import BaseModel


class Flower(BaseModel):
    name: str
    count: int
    cost: int
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    def get_all(self):
        return self.flowers
    
    def get_list_flowers(self, ids: list):
        flowers = []
        for id in ids:
            flowers.append(self.flowers[id - 1])
        return flowers

    def save(self, flower: Flower):
        flower.id = len(self.flowers) + 1
        self.flowers.append(flower)
        return flower.id
