from random import randint

from ramka import Vector, Game, Sprite, Input, Animation, pygame, copysign

Game.init('Рамка')
Game.цветФона = 200, 240, 200


class Plat(Sprite):

    def __init__(self, pik="ira_sprites/plat1.png"):
        super().__init__(pik)
        self.spd = Vector(0)
        self.x_lim = [0, Game.ширинаЭкрана]
        self.y_lim = [0, Game.высотаЭкрана]

    def update(self, deltaTime: float):
        self.transform.pos = self.transform.pos + self.spd * deltaTime

        v = self.get_size() * self.transform.scale.elementwise()
        if self.transform.x > self.x_lim[1] - v.x / 2 or self.transform.x < self.x_lim[0] + v.x / 2:
            self.spd.x = -self.spd.x
        if self.transform.y > self.y_lim[1] - v.y / 2 or self.transform.y < self.y_lim[0] + v.y / 2:
            self.spd.y = -self.spd.y


class Base(Sprite):
    ani = {
        "idle": Animation("ira_sprites/idle?.png", 5, True),
        "walk": Animation("ira_sprites/walk?.png", 5, True),
        "ski": Animation("ira_sprites/walk1.png", 5, True),
        "fly": Animation("ira_sprites/fly?.png", 5, True)
    }

    def __init__(self, igr):
        super().__init__(Base.ani)
        self.collision_image = pygame.image.load("ira_sprites/collider1.png").convert_alpha()
        self.vz = 1
        self.igr = igr
        self.state.animation = "walk"

        self.massa = 1
        self.max_spd = 250
        self.spd = Vector(0, 0)
        self.accel = [1000, 250]
        self.G = 900
        self.fric = [0.87, 1]
        self.jump_spd = 500
        self.max_spd_para = 80

        self.para = Sprite("ira_sprites/krila.png")
        self.para.transform.set_parent(self)
        self.para.transform.xy = 0, 0
        self.para.visible = False

        self.zg = Sprite("ira_sprites/morg.png")
        self.zg.transform.set_parent(self)
        self.zg.transform.xy = 0, 0
        self.zg.visible = False
        self.vm = self.time + randint(1,4)

        self.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана * 2 // 3
        # self.transform.scale_xy = 2, 2

    def on_enter_game(self):
        Game.add_object(self.para)
        self.para.change_order(-1)
        Game.add_object(self.zg)

    def on_leave_game(self):
        Game.remove_object(self.zg)
        Game.remove_object(self.para)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.zg.visible = self.time>self.vm and self.time<self.vm+0.2

        if not self.zg.visible and self.time>self.vm:
            self.vm = self.time + randint(1, 4)

        inair = 0 if self.is_grounded() else 1

        dx = Input.get("Horizontal" + self.igr)

        if Input.get("Jump" + self.igr) and not inair:
            self.spd.y -= self.jump_spd

        self.para.visible = Input.get("Jump" + self.igr) and inair and self.spd.y > 10

        f = Vector(dx * self.accel[inair], 0)

        a = f / self.massa
        if inair:
            a.y += self.G * (0.3 if self.para.visible else 1)

        self.spd = self.spd + a * deltaTime

        if abs(self.spd.x) > self.max_spd:
            self.spd.x = copysign(self.max_spd, self.spd.x)

        if self.para.visible and abs(self.spd.y) > self.max_spd_para:
            self.spd.y = copysign(self.max_spd_para, self.spd.y)

        if self.transform.parent:
            spd = self.spd / self.transform.parent.scale.elementwise()
        else:
            spd = self.spd
        self.transform.pos = self.transform.pos + spd * deltaTime

        if dx:
            self.vz = 1 if dx > 0 else -1
        else:
            self.spd *= self.fric[inair]

        self.state.animation = "fly" if inair else "walk" if dx else "idle" if self.spd.length_squared() < 25 else "ski"

        self.transform.scale_x = abs(self.transform.scale_x) * self.vz

    def is_grounded(self):
        r = False

        krai = Game.высотаЭкрана - self.get_size().y * self.transform.scale_y // 2
        if self.transform.y >= krai:
            self.transform.y = krai
            self.spd.y = 0
            r = True

        clue = False
        if not r:
            elev = 1

            if self.spd.y >= 0:
                pl = list(Game.get_objects(clas=Plat))
                cc = self.get_collided(pl, test_offset=Vector(0, elev))

                if len(cc) > 0:
                    r = True
                    clue = True
                    self.spd.y = 0

                    pl = [cc[0][0]]

                    vy = 0
                    while len(self.get_collided(pl, test_offset=Vector(0, vy + elev - 1))) > 0:
                        vy -= 1

                    self.transform.y = self.transform.y + vy

                    if self.transform.parent != pl[0]:
                        self.transform.set_parent(pl[0], True)

        if self.transform.parent and not clue:
            self.transform.detach(True)

        return r


plat = [
    (Game.ширинаЭкрана // 2 + 250, Game.высотаЭкрана - 400),
    (Game.ширинаЭкрана // 2 + 150, Game.высотаЭкрана - 300),
    (Game.ширинаЭкрана // 2 - 150, Game.высотаЭкрана - 200),
    (Game.ширинаЭкрана // 2 - 250, Game.высотаЭкрана - 100),
    (Game.ширинаЭкрана // 2 + 440, Game.высотаЭкрана - 400),
]

for i, p in enumerate(plat):
    plat1 = Plat()
    plat1.transform.xy = p
    if i == 1:
        plat1.spd = Vector(150, 0)
    if i == 4:
        plat1.spd = Vector(0, 50)
        plat1.transform.scale_x = 0.5
        plat1.y_lim = [70, plat1.transform.y + 16]

    Game.add_object(plat1)

ob = Plat("ira_sprites/oback.png")
ob.collision_image = pygame.image.load("ira_sprites/ocollider.png").convert_alpha()
ob.transform.xy = 120, 150
ob.spd = Vector(70, 0)
ob.transform.scale_xy = 7, 6
ob.x_lim = [0, Game.ширинаЭкрана - 250]
Game.add_object(ob)

girl = Base('1')
Game.add_object(girl)

girl = Base('2')
Game.add_object(girl)
girl.transform.scale_xy = 0.5, 0.5

hays = Sprite("ira_sprites/hays.png")
Game.add_object(hays)
hays.transform.xy = Game.ширинаЭкрана - hays.get_size().x, Game.высотаЭкрана - hays.get_size().y
hays.transform.scale_xy = 2, 2

obf = Sprite("ira_sprites/ofront.png")
obf.transform.set_parent(ob)
Game.add_object(obf)

Game.run()
