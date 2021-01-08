import math
from random import random
from typing import Dict

from ramka import pygame, Vector, FlipStyle, generate_flip, slice_image, Game, Sprite, Animation


class Test(Sprite):
    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        xx, yy = pygame.mouse.get_pos()
        angle = -Vector(10, 0).angle_to(Vector(xx, yy) - self.transform.pos)
        self.transform.angle = angle


class Animal(Sprite):

    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)
        self.vx = 1.0

    def get_flip(self) -> FlipStyle:
        return (self.vx > 0, False)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        # self.transform.look_at_ip(Vector(pygame.mouse.get_pos()),False)
        # self.vx = 1 if Vector(1, 0).rotate(self.transform.parent.angle if self.transform.parent else 0).y < 0 else -1
        # self.transform.x += self.vx * deltaTime * 80
        # self.transform.scale = (1 + 2 * abs(math.cos(self.time*0.2))) * Vector(1.0)
        if self.transform.parent and abs(self.transform.x) > 50:
            self.transform.x = math.copysign(50, self.transform.x)
            self.vx *= -1


Game.init('Рамка')

# === BOX
test_img = pygame.image.load("./sprites/test.png").convert_alpha()
test = Test({"default": Animation(generate_flip([test_img], (False, False)), 1, True)})
Game.add_object(test)
test.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана // 2
test.transform.scale_xy = 2, 2

# test.transform.rotate = 45
# === HYENAS
hyena_idle = pygame.image.load("./sprites/Hyena_idle.png")
hyena_walk = pygame.image.load("./sprites/Hyena_walk.png")

h_idle = Animation(generate_flip(slice_image(hyena_idle), (True, False)), 6, True)
h_walk = Animation(generate_flip(slice_image(hyena_walk), (True, False)), 12, True)

for i in range(10):
    hyena = Animal({"idle": h_idle, "default": h_walk})
    Game.add_object(hyena)
    hyena.transform.xy = 100 * random() - 50 // 2, test_img.get_height() / 2
    hyena.transform.scale = Vector(1 + (i == 0))
    hyena.image_offset.xy = 0, hyena_walk.get_height() / 2
    hyena.transform.set_parent(test)

# Game.drawOptions['show_offset']=True
# === RUN GAME
Game.run()

# todo: состояния
# todo: скорость анимации множитель
# todo: упрощеное создание анимаций
# todo: примитивы: круг, прямоугольник, точка, многоугольник
# todo: документация в коде
# todo: документация файл
