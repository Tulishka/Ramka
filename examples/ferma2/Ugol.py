from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Inventar import Inventar


class Ugol(Avtomat):
    def __init__(self):
        super().__init__("ira_sprites/steavugol.png",
                         product_type=4,
                         product_image=Inventar.item_images[4],
                         work_time=1,
                         )