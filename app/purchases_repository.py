from attrs import define


@define
class Purchase:
    user_id: int = 0
    flower_id: int = 0


class PurchasesRepository:
    purchases: list[Purchase]

    def __init__(self):
        self.purchases = []

    def save(self, purchase: Purchase):
        self.purchases.append(purchase)
        return purchase
    
    def get_by_user_id(self, user_id):
        purchases = []
        for purchase in self.purchases:
            if user_id == purchase.user_id:
                purchases.append(purchase.flower_id)
        return purchases