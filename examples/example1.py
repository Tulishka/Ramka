import math
from random import random
from typing import Dict

from ramka import pygame, Vector, FlipStyle, generate_flip, slice_image, Game, Sprite, Animation, Input, BoxCollider, \
    CircleCollider


class Area(Sprite):
    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

    def update(self, deltaTime: float):
        super().update(deltaTime)



class Box(Sprite):
    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)
        # self.add_component("box", BoxCollider(self, self.get_size()))
        self.add_component("circle", CircleCollider(self, max(0.5 * self.get_size())))

    def update(self, deltaTime: float):
        super().update(deltaTime)

        # xx, yy = pygame.mouse.get_pos()
        # angle = -Vector(10, 0).angle_to(Vector(xx, yy) - self.transform.pos)
        # self.transform.angle = angle

        # if Input.get("Jump"):
        #     self.transform.move_toward_ip(Vector(xx, yy), 80 * deltaTime, True)
            # self.transform.move_forward_ip(80*deltaTime)

        v = 500 * deltaTime * Vector(Input.get("Horizontal"), Input.get("Vertical"))
        # v.rotate_ip(-self.transform.angle)

        self.transform.pos = self.transform.pos + v


class Animal(Sprite):

    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

        self.vx = 1.0
        self.add_component("circle", CircleCollider(self, max(0.5 * self.get_size()), self.image_offset,
                                                    self.image_rotate_offset))
        # self.add_component("box", BoxCollider(self, self.get_size(), self.image_offset, self.image_rotate_offset))

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
test_img = pygame.image.load("./sprites/test.png").convert_alpha()

# === area
area = Area({"default": Animation(generate_flip([test_img], (False, False)), 1, True)})
Game.add_object(area)
area.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана // 2
area.transform.scale_xy = 2, 2

# === BOX
box = Box({"default": Animation(generate_flip([test_img], (False, False)), 1, True)})
Game.add_object(box)
box.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана // 2
box.transform.scale_xy = 0.5, 0.5

# test.transform.rotate = 45
# === HYENAS
hyena_idle = pygame.image.load("./sprites/Hyena_idle.png")
hyena_walk = pygame.image.load("./sprites/Hyena_walk.png")

h_idle = Animation(generate_flip(slice_image(hyena_idle), (True, False)), 6, True)
h_walk = Animation(generate_flip(slice_image(hyena_walk), (True, False)), 12, True)

for i in range(1):
    hyena = Animal({"idle": h_idle, "default": h_walk})
    Game.add_object(hyena)
    hyena.transform.xy = 80 * random() - 40, test_img.get_height() / 2
    hyena.transform.scale = Vector(1 + (i == -1))
    hyena.image_offset.xy = 0, hyena_walk.get_height() / 2
    hyena.transform.set_parent(area)

# Game.drawOptions['show_offset']=True
# === RUN GAME
Game.run()

# todo: состояния
# todo: скорость анимации множитель
# todo: упрощеное создание анимаций
# todo: компоненты
# todo: коллайдер
# todo: физика
# todo: звуки
# todo: примитивы: круг, прямоугольник, точка, многоугольник, пустой
# todo: документация в коде
# todo: документация файл
# todo: сообщения всем, паренту, чилдам. Сообщения pygame?
# todo: input.events
# todo: свойства кадрам анимации: обработчики, отправка событий
# todo: тригеры
# todo: game_object: before_update, after_update


# todo: move forvard, move toward
