import math
import random
from random import randint

import pygame

from ramka import *
from ramka.effects import Effects
from ramka.timeline import Timeline, TimeLineProgressInfo
from ramka.trigger import Trigger

Game.init('Пчелка')
Game.цветФона = 200, 200, 255


class Swarm(Sprite):

    def draw(self, dest: pygame.Surface):
        color = 0x0f, 0x0d, 0x02
        p = self.transform.get_world_transform().pos
        pygame.draw.rect(dest, color, pygame.Rect(p.x - 2, 0, 4, p.y - 48))
        super().draw(dest)


def default_particle_check(particle):
    if particle.pos.x > Game.ширинаЭкрана or particle.pos.x < 0:
        particle.velocity.x *= -1

    if particle.pos.y > Game.высотаЭкрана or particle.pos.y < -Game.высотаЭкрана * 0.1:
        particle.life_time = 0


class Particle: ...


class Particle:
    particles = []

    def __init__(self, pos: Vector, velocity: Vector, life_time: float, size: int, color: pygame.Color, mass: float = 1,
                 live_check=default_particle_check):
        self.pos = Vector(pos)
        self.size = size
        self.color = color
        self.velocity = Vector(velocity)
        self.life_time = life_time
        self.kill_borders = (0, 0, 0, 0)
        self.bounce_borders = (1, 1, 1, 1)
        self.auto_kill = True
        self.mass = mass
        self.bounce = 1.0
        self.live_check = default_particle_check

    def update(self, deltaTime: float, g_force: Vector):
        self.life_time -= deltaTime
        if self.life_time <= 0:
            self.life_time = 0
        else:
            self.velocity += g_force / self.mass
            self.pos += self.velocity * deltaTime

        self.live_check(self)

    def draw(self, dest: pygame.Surface):
        pygame.draw.circle(dest, self.color, self.pos, self.size)

    @staticmethod
    def add_particle(particle: Particle):
        Particle.particles.append(particle)

    @staticmethod
    def update_all(deltaTime: float, g_force: Vector = Vector(0, 9)):
        delet = []
        for p in Particle.particles:
            p.update(deltaTime, g_force)
            if p.life_time <= 0:
                delet.append(p)

        for p in delet:
            Particle.particles.remove(p)

    @staticmethod
    def draw_all(dest: pygame.Surface):
        for p in Particle.particles:
            p.draw(dest)


class Flower(Sprite):

    def __init__(self, animations: Union[Animation, pygame.Surface, Dict[str, Animation]]):
        super().__init__(animations)

        self.start_pos = None
        self.impulse = Vector(0)
        self.touched = False
        self.particle_per_impulse_k = 2
        self.particle_spawn_timeout = 0
        self.old_impulse = Vector(0)
        self.grow_timeout = randint(1, 50)

    def update(self, deltaTime: float):

        self.grow_timeout -= deltaTime
        if self.grow_timeout <= 0:
            self.grow_timeout = randint(10, 50)
            self.start_pos.y = randint(int(Game.высотаЭкрана * 0.3), int(Game.высотаЭкрана * 0.9))
            self.impulse += Vector(0, 1)

        if self.start_pos and self.impulse.length_squared() > 0:
            self.transform.pos = self.transform.pos + self.impulse * deltaTime

            self.transform.angle = min(0.5 * (self.transform.x - self.start_pos.x), 10)
            self.impulse *= 0.97

            f = self.start_pos - self.transform.pos
            self.impulse += f * 100 * deltaTime

            if self.impulse.length_squared() > 10000:
                self.impulse.scale_to_length(100)

            if self.impulse.length_squared() < 0.1 and f.length_squared() < 0.01:
                self.impulse = Vector(0)
                self.transform.pos = self.start_pos
            else:
                self.particle_spawn_timeout -= deltaTime
                if self.particle_spawn_timeout <= 0:
                    self.particle_spawn_timeout = 0.2
                    imp = self.impulse - self.old_impulse
                    self.spawn_particle(imp)
                    self.old_impulse = Vector(self.impulse)

        c = self.get_collided(Game.get_objects(filter=lambda x: isinstance(x, Bee) or isinstance(x, Pollen)))
        if len(c):
            if not self.touched:
                o = c[0][0]
                self.apply_impulse(Vector(o.скорость.x, o.скорость.y) * 0.5)
                self.touched = True
                if o.transform.y > self.transform.y and o.скорость.y < -o.максСкорость * 0.5:
                    o.скорость *= -0.5
                else:
                    o.скорость *= 0.8
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

    def apply_impulse(self, impulse: Vector):
        self.impulse += impulse
        self.spawn_particle(impulse)

    def spawn_particle(self, impulse: Vector):
        sz = self.get_size()
        sz = int(sz[0] // 4), int(sz[1] // 6)
        t = self.transform.get_world_transform()
        for i in range(int(self.particle_per_impulse_k * impulse.magnitude() * 0.05)):
            p = Vector(randint(-sz[0], sz[0]), randint(-sz[1], sz[1]))
            Particle.add_particle(Particle(t.add_to_vector(p), -1 * impulse, 10, randint(1, 3),
                                           pygame.Color(180 + randint(-10, 10), 190 + randint(-10, 10), 0)))


class Pollen(Sprite):
    def __init__(self, animations: Union[Animation, pygame.Surface, Dict[str, Animation]]):
        super().__init__(animations)

        self.collision_image = self.curr_animation().get_image(0)
        self.collision_image_transformable = False
        self.скорость = Vector(0)
        self.максСкорость = 400
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
            self.transform.angle = int(self._количество * 720) // 45 * 45

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
                        o.apply_impulse(8 * Vector(self.image_offset))
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
            if self.скорость.length_squared() > self.максСкорость * self.максСкорость:
                self.скорость.scale_to_length(self.максСкорость)

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

    pollen_pic = pygame.image.load("./sprites/pollen.png").convert_alpha()

    def __init__(self, control_suff="", a_scale=1.0):
        super().__init__(Bee.bee_ani)

        self.Направление = False
        self.максСкорость = 200 + randint(0, 50)
        self.Ускорение = 100 + randint(0, 50)
        self.скорость = Vector(0)
        self.control_suff = control_suff

        self.ТочкаДрейфа = Vector(0)
        self.СкоростьДрейфа = 20
        self.ВременнойСдвигДрейфа = randint(0, 50) / 25

        self.pollen = self.create_pollen()

        self.auto_harvest = False
        self.auto_dest = None
        self.auto_dest_offset = Vector(0.0)
        self.swarm = list(Game.get_objects(clas=Swarm))
        if len(self.swarm) > 0:
            self.swarm = self.swarm[0]
        else:
            self.swarm = self

        self.a_scale = a_scale if a_scale else 1
        self.transform.scale_xy = self.a_scale, self.a_scale

        self.eff=Effects(self)

    @Game.on_message(name="trigger.enter")
    def trex1(self, *a):
        self.transform.angle=self.transform.angle+20
        print("enter")

    @Game.on_message(name="trigger.exit")
    def trex2(self, *a):
        self.transform.angle = self.transform.angle-20
        print("exit")

    def create_pollen(self):
        pollen = Pollen(Bee.pollen_pic)
        Game.add_object(pollen)
        pollen.transform.xy = -7, 14
        pollen.transform.set_parent(self)
        pollen.количество = 0

        return pollen

    def drop_pollen(self):
        if self.pollen.количество > 0:
            p = self.create_pollen()
            p.количество = self.pollen.количество
            p.transform.detach(True)
            p.скорость = Vector(self.скорость)
            self.pollen.количество = 0

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.auto_harvest:
            if self.auto_dest is None and self.pollen.количество > self.pollen.min_size:
                if self.transform.pos.distance_squared_to(self.swarm.transform.pos) < 400:
                    self.auto_dest = self.swarm
            if self.auto_dest is None and self.pollen.количество < self.pollen.max_size:
                self.auto_dest = random.choice(list(Game.get_objects(clas=Flower)))
            if self.pollen.количество >= self.pollen.max_size:
                self.auto_dest = self.swarm

        if Input.get("Jump" + self.control_suff):
            self.drop_pollen()

        if self.auto_dest is None:
            dp = Vector(Input.get("Horizontal" + self.control_suff),
                        Input.get("Vertical" + self.control_suff)) * self.Ускорение
            spd = self.скорость.length_squared()
            if dp.x:
                self.Направление = dp.x >= 0
        else:
            if isinstance(self.auto_dest, GameObject):
                dest = self.auto_dest.transform.pos
            else:
                dest = self.auto_dest

            dif = dest - self.transform.pos + self.auto_dest_offset * self.transform.scale.elementwise()
            spd = self.скорость.length()
            stop_time = spd / self.Ускорение
            stop_dist = spd * stop_time + self.Ускорение * (stop_time ** 2) / 2
            dst = dif.length_squared()
            if dst > stop_dist * stop_dist:
                dif.scale_to_length(self.Ускорение)
                dp = dif
            else:
                dp = Vector(0)

            if dst < 100 and spd < 20:
                self.auto_dest = None

            if dp.x and spd > 10:
                self.Направление = self.скорость.x >= 0

        if dp.length_squared() < 0.1 and spd > 0:
            dp = -self.скорость
            dp.scale_to_length(min(spd, self.Ускорение))

        self.скорость += dp * deltaTime

        if self.скорость.length_squared() > self.максСкорость * self.максСкорость:
            self.скорость.scale_to_length(self.максСкорость)

        if self.ВременнойСдвигДрейфа - self.time < 0:
            self.ВременнойСдвигДрейфа = self.time + 0.5
            # self.ТочкаДрейфа = Vector(randint(0, Game.ширинаЭкрана), randint(0, Game.высотаЭкрана))
            obj = list(Game.get_objects(clas=Bee, filter=lambda p: p.control_suff == self.control_suff))
            if len(obj):
                sr = Vector(0.0)
                for o in obj:
                    sr += o.transform.pos
                sr *= 1 / len(obj)
                self.ТочкаДрейфа = sr + Vector(randint(-60, 60), randint(-60, 60))
            else:
                self.ТочкаДрейфа = Vector(randint(0, Game.ширинаЭкрана), randint(0, Game.высотаЭкрана))

        if self.скорость.length_squared() < 70:
            # self.скорость *= 0.97
            dv = self.ТочкаДрейфа - self.transform.pos
            dv.scale_to_length(self.СкоростьДрейфа)
        else:
            dv = Vector(0)

        self.transform.pos += (dv + self.скорость) * deltaTime

        if self.transform.x > Game.ширинаЭкрана or self.transform.x < 0:
            self.скорость.x *= -1
            self.transform.x += self.скорость.x * deltaTime
            self.drop_pollen()

        if self.transform.y > Game.высотаЭкрана or self.transform.y < 0:
            self.скорость.y *= -1
            self.transform.y += self.скорость.y * deltaTime
            self.drop_pollen()

        self.transform.scale_x = math.copysign(self.transform.scale_x, -1 if self.Направление else 1)

    # def draw(self, dest: pygame.Surface):
    #     super().draw(dest)
    #     pygame.draw.circle(dest,(255,0,0),self.ТочкаДрейфа,2)


class Spider(Sprite):
    pics_walk = [
        pygame.image.load("./sprites/spider_walk1.png").convert_alpha(),
        pygame.image.load("./sprites/spider_walk2.png").convert_alpha(),
        pygame.image.load("./sprites/spider_walk3.png").convert_alpha()
    ]

    walk_ani = Animation(pics_walk, 10, True)

    ani = {
        "walk": walk_ani
    }

    def __init__(self):
        super().__init__(Spider.ani)

        self.Направление = False
        self.максСкорость = 100 + randint(0, 50)
        self.Ускорение = 100 + randint(0, 50)
        self.скорость = Vector(self.максСкорость, 0)

        self.точкаНазначения = Vector(0)
        self.времяОжидания = randint(3, 15)

        self.eff = Effects(self)

        Timeline(self).do(self.jjj, duration=0.6).repeat(7).kill()

    @Game.on_key_down(key=pygame.K_1)
    def jjj(self, *arg):
        self.eff.hop()

    @Game.on_key_down(key=pygame.K_2)
    def jjj2(self, *arg):
        self.eff.pulse()

    @Game.on_key_down(key=pygame.K_3)
    def jjj3(self, *arg):
        self.eff.flip()

    def update(self, deltaTime: float):

        if self.transform.x > Game.ширинаЭкрана or self.transform.x < 0:
            self.скорость.x = -self.скорость.x

        if self.transform.y > Game.высотаЭкрана or self.transform.y < 0:
            self.скорость.y = -self.скорость.y

        self.transform.pos += self.скорость * deltaTime

        self.Направление = self.скорость.x > 0

        self.transform.scale_x = math.copysign(self.transform.scale_x, -1 if self.Направление else 1)

        Game.debug_str = str(len(self.components))

        super().update(deltaTime)


class Dummy(GameObject):
    def __init__(self, pos):
        super().__init__()
        self.transform.pos = pos
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))

    def update(self, deltaTime: float):
        super().update(deltaTime)

    def draw(self, dest: pygame.Surface):
        pygame.draw.circle(dest, self.color, self.screen_pos(), 40)


# СОЗДАНИЕ УЛЕЯ ==============
swarm_pic = pygame.image.load("./sprites/swarm.png").convert_alpha()

swarm = Swarm(swarm_pic)
Game.add_object(swarm)
swarm.transform.pos = Vector(Game.ширинаЭкрана - 100, 100)
swarm.transform.scale_xy = 5, 5

# СОЗДАНИЕ ЦВЕТКОВ ==============
flower_pic = pygame.image.load("./sprites/flower.png").convert_alpha()
flower_collider = pygame.image.load("./sprites/flower_collider.png").convert_alpha()

flower_count = 7
for i in range(flower_count):
    flower = Flower(flower_pic)
    Game.add_object(flower)
    flower.collision_image = flower_collider
    flower.transform.pos = Vector((i + 1) * (Game.ширинаЭкрана / (flower_count + 1)) - flower.get_size()[0],
                                  Game.высотаЭкрана * 0.7 + randint(-int(Game.высотаЭкрана * 0.2),
                                                                    int(Game.высотаЭкрана * 0.2)))
    flower.start_pos = Vector(flower.transform.pos)
    flower.transform.scale_xy = 3, 3

# СОЗДАНИЕ КОРОЛЕВЫ ==============
qwin_bee = Bee("1", 2)
Game.add_object(qwin_bee)
qwin_bee.transform.xy = 100, 100

qwin_bee.auto_harvest = True
qwin_bee.auto_dest_offset = Vector(4, -16)

# СОЗДАНИЕ КОРОНЫ ==============
crown_pic = pygame.image.load("./sprites/crown.png").convert_alpha()
crown = Sprite(crown_pic)
Game.add_object(crown)
crown.transform.xy = -10, -10
crown.transform.set_parent(qwin_bee)

# bee = Bee("1")
# Game.add_object(bee)
# bee.transform.xy = qwin_bee.transform.x + randint(-50, 50), qwin_bee.transform.y + randint(-50, 50)
# bee.transform.scale_xy = 0.4, 0.4

# СОЗДАНИЕ ПЧЕЛОК ==============
for i in range(10):
    a = randint(1, 5) / 10
    bee = Bee("2", 0.5 + a)
    Game.add_object(bee)
    bee.transform.xy = 50 + randint(0, 100), 50 + randint(0, 100)
    bee.auto_harvest = True
    bee.auto_dest_offset = Vector(4, -16)

# СОЗДАНИЕ ПАУКА ================
spider = Spider()
Game.add_object(spider)
spider.transform.xy = 100, Game.высотаЭкрана - 48
spider.transform.scale_xy = 3, 3


# hat=Sprite(flower_pic)
# Game.add_object(hat)
# hat.transform.set_parent(spider)
# hat.transform.scale_xy=0.5,0.5
# hat.transform.y=-13
# hat.transform.angle=-15

@Game.after_update
def game_update(deltaTime):
    Particle.update_all(deltaTime)


@Game.after_draw
def game_update(disp):
    Particle.draw_all(disp)


# p = Dummy((400, 400))
# Game.add_object(p)
# p.color=(0,0,0)
#
# c = Dummy((120, 120))
# c.transform.set_parent(p)
# c.color=(255,0,0)
# Game.add_object(c)
# c.parent_sort_me_by="_"
#
# for d in range(1,6):
#     c = Dummy((d * 20, d * 20))
#     c.color = (d*20,d*20,d*20)
#     c.opacity=0.5
#     c.transform.set_parent(p)
#     Game.add_object(c)

# Game.defaultLayer.change_order_last(p)
# Game.defaultLayer.sort_object_children(p)


cam = Camera()
Game.add_object(cam)
# cam.set_focus(d, lock_y=True)

Game.add_object(Trigger("triger 1", parent=qwin_bee, color=(255, 0, 0)).set_n_poly(5, 180).set_watch_for(ObjectFilter(clas=Flower)))



Game.run()
