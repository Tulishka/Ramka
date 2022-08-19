from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Inventar import Inventar
from ramka import Sprite, Game


class Melinica(Avtomat):
    def __init__(self):
        super().__init__("ira_sprites/steavmelinica1.png",
                         product_type=2,
                         product_image=Inventar.item_images[2],
                         required_res={1: 1},
                         work_time=2
                         )

        self.loposti = Sprite("ira_sprites/steavmelinica2.png")
        self.loposti.transform.set_parent(self)
        self.loposti.transform.y = -70
        self.spdp = 5

    def on_enter_game(self):
        Game.add_object(self.loposti)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        dl = self.spdp * (4 if self.onduty else 1) * deltaTime
        df = 360 * dl / (6.28 * 6 * self.transform.scale_x)
        self.loposti.transform.angle -= df