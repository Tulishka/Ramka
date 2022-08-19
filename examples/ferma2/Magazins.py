from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Inventar import Inventar
from ramka import Sprite


class Magazin2(Avtomat):
    def __init__(self):
        super().__init__("ira_sprites/steavmagaz2.png",
                         product_type=0,
                         product_image=Inventar.item_images[0],
                         required_res={5: 1},
                         work_time=0.2,
                         product_count=3
                         )


class Magazin1(Avtomat):
    def __init__(self):
        super().__init__("ira_sprites/steavmagaz1.png",
                         product_type=5,
                         product_image=Inventar.item_images[5],
                         required_res={3: 2},
                         work_time=0.2
                         )


class Kafe(Sprite):
    def __init__(self):
        super().__init__("ira_sprites/steavkafe.png")
