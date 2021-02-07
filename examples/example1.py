import math
from random import random
from typing import Dict

from ramka import pygame, Vector, FlipStyle, slice_image, Game, Sprite, Animation, Input


class Area(Sprite):
    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        v = 180 * deltaTime * Input.get("Rotate")

        self.transform.angle = self.transform.angle + v


class Box(Sprite):
    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        v = 800 * deltaTime * Vector(Input.get("Horizontal"), Input.get("Vertical"))
        self.transform.pos = self.transform.pos + v


class Animal(Sprite):

    def __init__(self, animations: Dict[str, Animation]):
        super().__init__(animations)

        # self.add_component( BoxCollider(self,Vector(48,48), Vector(0,-24)))

        self.vx = 1.0
        self.lc = (0, 0)

    def get_flip(self) -> FlipStyle:
        return self.vx > 0, False

    def update(self, deltaTime: float):
        # super().update(deltaTime)

        # self.transform.look_at_ip(Vector(pygame.mouse.get_pos()),False)
        # self.vx = 1 if Vector(1, 0).rotate(self.transform.parent.angle if self.transform.parent else 0).y < 0 else -1

        # self.transform.x += self.vx * deltaTime * 80

        lst = list(Game.get_objects(clas=Box))
        c = self.get_collided(lst)

        vy = 0
        if len(c):
            vy = -50

        while vy < 50:
            z = self.get_collided(lst, test_offset=Vector(0, 1 + vy))
            if len(z):
                self.lc = z[0][1]
                break
            vy = vy + 1

        # vy=vy * 200 * deltaTime
        wtr = self.transform.get_world_transform()
        wtr.y = wtr.y + vy

        v = self.transform.to_parent_local_coord(Vector(wtr.x, wtr.y), False)
        self.transform.xy = v

        # self.transform.scale = (1 + 2 * abs(math.cos(self.time*0.2))) * Vector(1.0)
        # if self.transform.parent and abs(self.transform.x) > 50:
        #     self.transform.x = math.copysign(50, self.transform.x)
        #     self.vx *= -1

    def draw(self, dest: pygame.Surface):
        super().draw(dest)
        p0=Vector(self.lc[0], self.lc[1])
        p1=self.image_pos_to_global(p0)
        p2=self.global_to_image_pos(p1)
        Game.debug_str = f'({round(p1.x-p2.x)},{round(p1.y-p2.y)})'
        pygame.draw.circle(dest, (255, 0, 0), p1, 2)


Game.init('Рамка')
test_img = pygame.image.load("./sprites/test.png").convert_alpha()

# === area
area = Area({"default": Animation([test_img], 1, True)})
Game.add_object(area)
area.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана // 2
area.transform.scale_xy = 2, 2
# area.transform.angle=90

# === BOX
box = Box({"default": Animation([test_img], 1, True)})
Game.add_object(box)
box.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана // 2
box.transform.scale_xy = 5, 0.5

# test.transform.rotate = 45
# === HYENAS
hyena_idle = pygame.image.load("./sprites/Hyena_idle.png")
hyena_walk = pygame.image.load("./sprites/Hyena_walk.png")

h_idle = Animation(slice_image(hyena_idle), 6, True)
h_walk = Animation(slice_image(hyena_walk), 12, True)

hyena = Animal({"idle": h_idle, "default": h_walk})
Game.add_object(hyena)
hyena.transform.xy = (0, 0)
hyena.image_offset.xy = 0, hyena_walk.get_height() / 2
hyena.transform.set_parent(area)

# Game.drawOptions['show_offset']=True
# === RUN GAME
Game.run()

# todo: состояния
# todo: скорость анимации множитель
# todo: упрощеное создание анимаций
# todo: коллайдер : can collide
# todo: pymunk
# todo: звуки
# todo: примитивы: круг, прямоугольник, точка, многоугольник, пустой
# todo: документация в коде
# todo: документация файл
# todo: сообщения всем, паренту, чилдам. Сообщения pygame?
# todo: input.events
# todo: свойства кадрам анимации: обработчики, отправка событий
# todo: тригеры
# todo: game_object: before_update, after_update
# todo: pygame.Sprite, кэш в Animation (get image by time & transform)
