import math
from random import randint

from ramka import *

Game.init('Пчелка')
Game.цветФона = 200, 200, 255

bee_pics = [
    pygame.image.load("./sprites/bee1.png"),
    pygame.image.load("./sprites/bee2.png")
]

crown_pic = pygame.image.load("./sprites/crown.png")
swarm_pic = pygame.image.load("./sprites/swarm.png")

bee_fly_ani = Animation(bee_pics, 17, True)

bee_ani = {
    "fly": bee_fly_ani
}


class Bee(Sprite):

    def __init__(self):
        super().__init__(bee_ani)

        self.Направление = False
        self.МаксСкорость = 200 + randint(0, 50)
        self.Ускорение = 100 + randint(0, 50)
        self.Скорость = Vector(0)

        self.ТочкаДрейфа = Vector(0)
        self.СкоростьДрейфа = 20
        self.ВременнойСдвигДрейфа = randint(0, 50) / 25

    def update(self, deltaTime: float):
        super().update(deltaTime)

        dp = Vector(self.Ускорение * Input.get("Horizontal"), self.Ускорение * Input.get("Vertical"))

        self.Скорость += dp * deltaTime

        if self.Скорость.length_squared() > self.МаксСкорость * self.МаксСкорость:
            self.Скорость.scale_to_length(self.МаксСкорость)

        self.transform.pos = self.transform.pos + self.Скорость * deltaTime

        if dp.x:
            self.Направление = dp.x >= 0

        if dp.length_squared() < 1:
            self.Скорость *= 0.97

        if self.ВременнойСдвигДрейфа - self.time < 0:
            self.ВременнойСдвигДрейфа = self.time + 0.5
            self.ТочкаДрейфа = Vector(randint(0, Game.ширинаЭкрана), randint(0, Game.высотаЭкрана))

        dv = self.ТочкаДрейфа - self.transform.pos
        dv.scale_to_length(self.СкоростьДрейфа)

        self.transform.pos += dv * deltaTime

        if self.transform.x > Game.ширинаЭкрана or self.transform.x < 0:
            self.Скорость.x *= -1
            self.transform.x = self.transform.x + self.Скорость.x * deltaTime

        if self.transform.y > Game.высотаЭкрана or self.transform.y < 0:
            self.Скорость.y *= -1
            self.transform.y = self.transform.y + self.Скорость.y * deltaTime

        self.transform.scale_x = math.copysign(self.transform.scale_x, -1 if self.Направление else 1)

    # def draw(self, dest: pygame.Surface):
    #     super().draw(dest)
    #     pygame.draw.circle(dest,(255,0,0),self.ТочкаДрейфа,2)


class Swarm(Sprite):

    def draw(self, dest: pygame.Surface):
        color = 0x0f, 0x0d, 0x02
        p = self.transform.get_world_transform().pos
        pygame.draw.rect(dest, color, pygame.Rect(p.x - 2, 0, 4, p.y - 48))
        super().draw(dest)


# СОЗДАНИЕ УЛЕЯ ==============
swarm = Swarm(swarm_pic)
Game.add_object(swarm)
swarm.transform.pos = (Game.ширинаЭкрана - 100, 100)
swarm.transform.scale_xy = 5, 5

# СОЗДАНИЕ ПЧЕЛОК ==============
for i in range(1):
    bee = Bee()
    Game.add_object(bee)
    bee.transform.x = 50 + randint(0, 100)
    bee.transform.y = 50 + randint(0, 100)

# СОЗДАНИЕ КОРОЛЕВЫ ==============
qwin_bee = Bee()
Game.add_object(qwin_bee)
qwin_bee.Ускорение *= 1
qwin_bee.transform.x = 100
qwin_bee.transform.y = 100
qwin_bee.transform.scale_xy = 2, 2

# СОЗДАНИЕ КОРОНЫ ==============
crown = Sprite(crown_pic)
Game.add_object(crown)
crown.transform.x = -10
crown.transform.y = -10
crown.transform.set_parent(qwin_bee)

Game.run()
