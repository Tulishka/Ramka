import math
from random import random
from typing import Dict

from Ramka import pygame, Vector, FlipStyle, generate_flip, slice_image, Game, Sprite, RotationNone, \
     RotationFree, RotationFlip, RotationTarget, Animation

class Test(Sprite):
    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        xx, yy = pygame.mouse.get_pos()
        angle = -Vector(10, 0).angle_to(Vector(xx, yy) - test.transform.pos)
        test.transform.rotate = angle


class Animal(Sprite):

    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)
        self.vx = 1.0

    def get_flip(self) -> FlipStyle:
        return (self.vx > 0, False)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.vx = 1 if Vector(1, 0).rotate(self.parent.transform.rotate if self.parent else 0).y < 0 else -1
        self.transform.pos.x += self.vx * deltaTime * 80
        if abs(self.transform.pos.x) > 50:
            self.transform.pos.x = math.copysign(50, self.transform.pos.x)


game = Game('Рамка')

# === BOX
test_img = pygame.image.load("./sprites/test.png").convert_alpha()
test = Test({"default": Animation(generate_flip([test_img], (False, False)), 1, True)})
game.add_object(f"test", test)
test.transform.pos.xy = game.ширинаЭкрана // 2, game.высотаЭкрана // 2
test.transform.scale.xy = 2,2


# === HYENAS
hyena_idle = pygame.image.load("./sprites/Hyena_idle.png")
hyena_walk = pygame.image.load("./sprites/Hyena_walk.png")

h_idle = Animation(generate_flip(slice_image(hyena_idle), (True, False)), 6, True)
h_walk = Animation(generate_flip(slice_image(hyena_walk), (True, False)), 12, True)

# tf=RotationTarget(Vector(0,0)).transform

for i in range(10):
    hyena = Animal({"idle": h_idle, "default": h_walk})
    game.add_object(f"hyena{i}", hyena, test)
    hyena.transform.pos.xy = test_img.get_width() * random() - test_img.get_width() // 2, test_img.get_height() / 2
    hyena.transform.offset.xy = 0, hyena_walk.get_height() / 2
    # hyena.transform.modifier_func = tf
# === RUN GAME
game.run()


# todo: стиль вращения: нет, отражение (ХХ / YY / XY), свободное вращение (дискрет), готовые направления (угол), цель (трансформ), свое
# todo: сортировка объектов
# todo: группы / слои, сортировка слоев
# todo: упрощеное создание анимаций
# todo: состояния
# todo: оптимизация: кэширование, невидимые объекты

