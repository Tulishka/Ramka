from examples.Components.mini_map import MiniMapItem
from examples.ferma2.Kost import Kost
from ramka import Sprite, Animation, Game


class PetIcon(MiniMapItem):
    def get_color(self):
        return (255, 0, 0)


class Pet(PetIcon, Sprite):
    def anim(self):
        return {
            "idle": Animation("ira_sprites/pets.png", 5, True),
            "walk": Animation("ira_sprites/pet.png", 5, True),
        }

    def __init__(self, igr):
        super().__init__(self.anim())
        self.spd = 250
        self.igr = igr
        self.radius = 60

    def update(self, deltaTime: float):
        super().update(deltaTime)
        kost = list(Game.get_objects(clas=Kost))
        if len(kost) <= 0:
            if (self.igr.transform.pos - self.transform.pos).length_squared() > self.radius * self.radius:
                self.transform.move_toward_ip(self.igr, self.spd * deltaTime)
                self.state.animation = "walk"
                self.transform.scale_x = 1 if self.transform.x > self.igr.transform.x else -1
            else:
                self.state.animation = "idle"
        else:
            if kost[0].transform.parent != self.transform:
                self.transform.move_toward_ip(kost[0], self.spd * deltaTime)

                self.transform.scale_x = 1 if self.transform.x > kost[0].transform.x else -1

                if kost[0].ready and self.is_collided(kost[0]):
                    kost[0].transform.set_parent(self)
                    kost[0].transform.pos = 0, 0
                    kost[0].transform.angle = -45

            else:
                self.transform.move_toward_ip(self.igr, self.spd * deltaTime)
                self.transform.scale_x = 1 if self.transform.x > self.igr.transform.x else -1

            self.state.animation = "walk"
