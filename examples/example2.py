import math
from random import randint

from ramka import *

Game.init('Пчелка')
Game.цветФона = 200, 200, 255


class Swarm(Sprite):

    def draw(self, dest: pygame.Surface):
        color = 0x0f, 0x0d, 0x02
        p = self.transform.get_world_transform().pos
        pygame.draw.rect(dest, color, pygame.Rect(p.x - 2, 0, 4, p.y - 48))
        super().draw(dest)


class Flower(Sprite):

    def __init__(self, animations: Union[Animation, pygame.Surface, Dict[str, Animation]]):
        super().__init__(animations)

        self.start_pos = None
        self.impulse = Vector(0)
        self.touched = False

    def update(self, deltaTime: float):

        if self.start_pos and self.impulse.length_squared() > 0:
            self.transform.pos = self.transform.pos + self.impulse * deltaTime

            self.transform.angle = min(0.5 * (self.transform.x - self.start_pos.x), 10)
            self.impulse *= 0.97

            f = self.start_pos - self.transform.pos
            self.impulse += f * 100 * deltaTime

            if self.impulse.length_squared() < 0.1 and f.length_squared() < 0.01:
                self.impulse = Vector(0)
                self.transform.pos = self.start_pos

        c = self.get_collided(Game.get_objects(clas=Bee))
        if len(c):
            if not self.touched:
                o = c[0][0]
                self.impulse = Vector(o.Скорость.x, o.Скорость.y) * 0.5
                self.touched = True
                if o.transform.y > self.transform.y and o.Скорость.y < -o.МаксСкорость * 0.5:
                    o.Скорость *= -0.5
                else:
                    o.Скорость *= 0.8
        else:
            self.touched = False

        super().update(deltaTime)

    def draw(self, dest: pygame.Surface):
        color = 0x00, 0x80, 0x4a
        p = self.transform.get_world_transform().pos

        if self.start_pos:
            pygame.draw.line(dest, color, p, (self.start_pos.x, Game.высотаЭкрана), 10)
        else:
            pygame.draw.rect(dest, color, pygame.Rect(p.x - 4, p.y + 24, 8, Game.высотаЭкрана - p.y - 24))

        super().draw(dest)


class Part(Sprite):
    def __init__(self, animations: Union[Animation, pygame.Surface, Dict[str, Animation]]):
        super().__init__(animations)

        self.collision_image = self.curr_animation().get_image(0)
        self.collision_image_transformable = False
        self.скорость = Vector(0)
        self._количество = 0
        self.transform.scale_xy = 0, 0
        self.max_size = 1.3
        self.min_size = 0.01

    @property
    def количество(self):
        return self._количество

    @количество.setter
    def количество(self, value):
        if value != self._количество:
            self._количество = value
            self.transform.scale_xy = self._количество, self._количество

    def update(self, deltaTime):
        super().update(deltaTime)

        if self.transform.parent:
            c = self.get_collided(Game.get_objects(filter=lambda x: isinstance(x, Flower) or isinstance(x, Swarm)))
            if len(c):
                o = c[0][0]
                if isinstance(o, Flower):
                    if self.количество < self.max_size:
                        self.image_offset.x = math.cos(self.time * 20)
                        self.image_offset.y = math.sin(self.time * 20)
                        o.impulse += 8 * Vector(self.image_offset)
                        self.количество += self.max_size / 5 * deltaTime
                    else:
                        self.количество = self.max_size

                else:
                    if self.количество > self.min_size:
                        self.image_offset.x = math.cos(-self.time * 20)
                        self.image_offset.y = math.sin(-self.time * 20)
                        self.количество -= self.max_size / 2 * deltaTime

                    if self.количество < self.min_size:
                        self.количество = self.min_size

        else:
            self.скорость.y += 200 * deltaTime
            self.transform.pos = self.transform.pos + self.скорость * deltaTime
            if self.transform.y > Game.высотаЭкрана:
                Game.remove_object(self)


class Bee(Sprite):
    bee_pics = [
        pygame.image.load("./sprites/bee1.png").convert_alpha(),
        pygame.image.load("./sprites/bee2.png").convert_alpha()
    ]

    bee_fly_ani = Animation(bee_pics, 17, True)

    bee_ani = {
        "fly": bee_fly_ani
    }

    part_pic = pygame.image.load("./sprites/part.png").convert_alpha()

    def __init__(self):
        super().__init__(Bee.bee_ani)

        self.Направление = False
        self.МаксСкорость = 200 + randint(0, 50)
        self.Ускорение = 100 + randint(0, 50)
        self.Скорость = Vector(0)

        self.ТочкаДрейфа = Vector(0)
        self.СкоростьДрейфа = 20
        self.ВременнойСдвигДрейфа = randint(0, 50) / 25

        self.part = self.create_part()

    def create_part(self):

        part = Part(Bee.part_pic)
        Game.add_object(part)
        part.transform.xy = -7, 14
        part.transform.set_parent(self)
        part.количество = 0

        return part

    def drop_part(self):
        p = self.create_part()
        p.количество = self.part.количество
        p.transform.detach(True)
        p.скорость = Vector(self.Скорость)
        self.part.количество = 0
        return p

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if Input.get("Jump"):
            self.drop_part()

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
            self.drop_part()

        if self.transform.y > Game.высотаЭкрана or self.transform.y < 0:
            self.Скорость.y *= -1
            self.transform.y = self.transform.y + self.Скорость.y * deltaTime
            self.drop_part()

        self.transform.scale_x = math.copysign(self.transform.scale_x, -1 if self.Направление else 1)

    # def draw(self, dest: pygame.Surface):
    #     super().draw(dest)
    #     pygame.draw.circle(dest,(255,0,0),self.ТочкаДрейфа,2)


# СОЗДАНИЕ УЛЕЯ ==============
swarm_pic = pygame.image.load("./sprites/swarm.png").convert_alpha()

swarm = Swarm(swarm_pic)
Game.add_object(swarm)
swarm.transform.pos = Vector(Game.ширинаЭкрана - 100, 100)
swarm.transform.scale_xy = 5, 5

# СОЗДАНИЕ ЦВЕТКОВ ==============
flower_pic = pygame.image.load("./sprites/flower.png").convert_alpha()
flower_collider = pygame.image.load("./sprites/flower_collider.png").convert_alpha()

flower_count = 6
for i in range(flower_count):
    flower = Flower(flower_pic)
    Game.add_object(flower)
    flower.collision_image = flower_collider
    flower.transform.pos = Vector((i + 1) * (Game.ширинаЭкрана / (flower_count + 1)) - flower.get_size()[0],
                                  Game.высотаЭкрана * 0.7 + randint(-int(Game.высотаЭкрана * 0.2),
                                                                    int(Game.высотаЭкрана * 0.2)))
    flower.start_pos = Vector(flower.transform.pos)
    flower.transform.scale_xy = 4, 4

# СОЗДАНИЕ ПЧЕЛОК ==============
for i in range(1):
    bee = Bee()
    Game.add_object(bee)
    bee.transform.xy = 50 + randint(0, 100), 50 + randint(0, 100)

# СОЗДАНИЕ КОРОЛЕВЫ ==============
qwin_bee = Bee()
Game.add_object(qwin_bee)
qwin_bee.Ускорение *= 1
qwin_bee.transform.xy = 100, 100
qwin_bee.transform.scale_xy = 2, 2

# СОЗДАНИЕ КОРОНЫ ==============
crown_pic = pygame.image.load("./sprites/crown.png").convert_alpha()
crown = Sprite(crown_pic)
Game.add_object(crown)
crown.transform.xy = -10, -10
crown.transform.set_parent(qwin_bee)

Game.run()
