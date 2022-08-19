from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Inventar import Inventar
from ramka import Animation


class Pech(Avtomat):
    def get_anim(self):
        return {
        "default": Animation("ira_sprites/steavpech.png", 5, True),
        "work": Animation("ira_sprites/steavpech2.png", 5, True),
    }

    def __init__(self):
        super().__init__(self.get_anim(),
                         product_type=3,
                         product_image=Inventar.item_images[3],
                         required_res={2: 1, 4: 1},
                         work_time=1,
                         product_count=2
                         )
        self.transform.scale = 2, 2

    def update(self, deltaTime: float):
        super().update(deltaTime)
        self.state.animation = "work" if self.onduty else "default"