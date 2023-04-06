from random import randint, choice, random

from ramka import Vector, Game, Sprite, Input, Animation, pygame, copysign, GameObject, math

Game.init('Рамка')
Game.цветФона = 200, 240, 200

class Hat(Sprite):

    def __init__(self,n, pik="ira_sprites/hat?.png"):
        super().__init__(pik)
        self.animations["default"].fps=0
        self.animations["default"].first_frame_index=n


    def update(self, deltaTime: float):
        super().update(deltaTime)


class Unicorn(Sprite):
    def __init__(self):
        super().__init__("ira_sprites/ang/pet*.png")

        self.owner = None
        self.owner_offset = Vector(-8, -16)  # смещение

        self.transform.scale_xy = 0.7, 0.7

        self.animations["default"].fps = 12

        self.vz = 1

        self.faza = random()

        # физика
        self.massa = 1
        self.max_spd = 230
        self.spd = Vector(0, 0)
        self.accel = 500
        self.fric = 0.87

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.owner is None:
            return

        # если рядом с моим хозяином  на рсстоянии 70 пикселей есть кристал то я лечу к нему и собираю его иначе лечу за хозяином
        # получить список кристалов которые рядом с игроком
        # if список не пустой:
        # узнать координаты кристала и задать dest
        #

        tr = self.owner.transform.get_world_transform()
        dest = tr.pos - 0.5 * self.get_size() + self.owner_offset * tr.scale.elementwise()
        dest.y += 5 * math.sin(4 * self.time + dest.x / 10 + self.faza)

        # dif = dest - self.transform.pos - 0.5 * Vector(copysign(self.get_size().x,tr.scale_x) ,self.get_size().y) + self.owner_offset * tr.scale.elementwise()



        cu =list (Game.get_objects(clas=Crystal, filter=lambda c: c.transform.pos.distance_to(tr.pos) <= 100))

        if len(cu) > 0:
            dest=cu[0].transform.pos


        dif = dest - self.transform.pos
        dst = dif.length_squared()

        if dst<100 and len(cu) > 0:
            cu[0].collect()
            self.owner.got_crystal()

        spd = self.spd.length()

        stop_time = spd / self.accel
        stop_dist = spd * stop_time + self.accel * (stop_time ** 2) / 2

        if dst > stop_dist * stop_dist:
            dif.scale_to_length(self.accel)
            dp = dif
        else:
            dp = Vector(0)

        if dst < 400:
            self.spd *= self.fric

        if dp.x and spd > 40:
            self.vz = -1 if self.spd.x >= 0 else 1
        else:
            if spd < 10:
                self.vz = 1 if self.transform.x > self.owner.transform.x else -1

        if dp.length_squared() < 0.1 and spd > 0:
            dp = -self.spd
            af = min(spd, self.accel)
            if af != 0:
                dp.scale_to_length(af)
            else:
                dp = Vector(0)

        a = dp / self.massa

        self.spd = self.spd + a * deltaTime

        if self.spd.length_squared() > self.max_spd * self.max_spd:
            self.spd.scale_to_length(self.max_spd)

        self.transform.pos = self.transform.pos + self.spd * deltaTime

        # if a.x:
        #     self.vz = 1 if a.x > 0 else -1
        # else:
        #     self.spd *= self.fric

        self.transform.scale_x = abs(self.transform.scale_x) * self.vz


class Totem(Sprite):
    def __init__(self):
        super().__init__("ira_sprites/statyia.png")

    def update(self, deltaTime: float):
        super().update(deltaTime)

        f = list(Game.get_objects(clas=Base))
        if len(f) > 0:
            cc = self.get_collided(f)
            if len(cc) > 0:
                ig = cc[0][0]
                c = list(Game.get_objects(clas=Unicorn, filter=lambda x: x.owner == ig))
                if len(c) < 3:

                    d = list(Game.get_objects(clas=Balloon, filter=lambda x: x.owner == ig))
                    if len(d) >= 4:
                        uni = Unicorn()
                        uni.transform.xy = Game.ширинаЭкрана, -1000
                        uni.owner = ig
                        Game.add_object(uni)

                        tl = (uni.transform.pos - ig.transform.pos).length() / uni.max_spd
                        tl *= 1.1
                        for s in d:
                            s.owner = uni
                            s.kill_time = s.time + tl


class Crystal(Sprite):
    def __init__(self):
        super().__init__("ira_sprites/cri?.png")
        self.time = random()
        self.transform.scale_xy = 2, 2
        self.collected=False

    def update(self, deltaTime: float):
        super().update(deltaTime)

    def collect(self):
        self.collected=True


class CrystalManager:
    poloj = [(750, 405), (858, 614), (321, 31)]
    bolls = [0 for i in poloj]
    time = 0
    spawn_time = 2

    @staticmethod
    def add_crystal(dt):
        CrystalManager.time += dt

        for n, i in enumerate(CrystalManager.bolls):
            if i != 0:
                if i.collected:
                    CrystalManager.bolls[n] = 0
                    Game.remove_object(i)

        if CrystalManager.time > CrystalManager.spawn_time:
            lst = [i for i, z in enumerate(CrystalManager.bolls) if z == 0]
            if len(lst) > 0:
                i = choice(lst)
                CrystalManager.bolls[i] = Crystal()
                CrystalManager.bolls[i].transform.xy = CrystalManager.poloj[i]
                Game.add_object(CrystalManager.bolls[i])
            CrystalManager.spawn_time = CrystalManager.time + 10


class Balloon(Sprite):
    def __init__(self):
        super().__init__("ira_sprites/harik.png")
        self.owner = None
        self.spd = 250
        self.faza = random()
        self.max_scale = 3
        self.transform.scale_xy = 0.1, 0.1
        self.kill_time = 50

    def update(self, deltaTime: float):

        super().update(deltaTime)

        if self.owner is None:

            if self.transform.scale_x < self.max_scale:
                self.transform.scale_xy = self.transform.scale_x + deltaTime * 3, self.transform.scale_y + deltaTime * 3
                if self.transform.scale_x > self.max_scale:
                    self.transform.scale_xy = self.max_scale, self.max_scale

            f = list(Game.get_objects(clas=Base))
            if len(f) > 0:
                cc = self.get_collided(f)
                if len(cc) > 0:
                    self.owner = cc[0][0]
                    self.transform.scale_xy = 3 * self.owner.transform.scale_x, 3 * self.owner.transform.scale_y

        else:
            if self.time > self.kill_time:
                self.owner = None
                Game.remove_object(self)
                return

            p = self.owner.transform.get_world_transform().pos

            hp = self.owner.get_size().y * self.owner.transform.scale_y / 2
            hb = self.get_size().y * self.transform.scale_y / 2
            h = hp + hb

            nnt = p - self.transform.pos + Vector(0, -h)
            dst = nnt.length()
            if dst > 0:
                nnt.normalize_ip()
                cc = self.spd * deltaTime
                if dst < cc:
                    cc = dst
                self.transform.pos = self.transform.pos + cc * nnt

        amp = 2 if self.owner else 1
        self.image_offset.x = amp * 2 * math.sin(self.time * 2 * amp + self.faza)
        self.image_offset.y = amp * math.cos(self.time * 1.6 * amp + 1.1 * self.faza)


class BalloonManager:
    poloj = [(35, 70), (970, 550), (55, 560), (418, 284)]
    bolls = [0 for i in poloj]
    time = 0
    spawn_time = 2

    @staticmethod
    def add_ball(dt):
        BalloonManager.time += dt

        for n, i in enumerate(BalloonManager.bolls):
            if i != 0:
                if i.owner:
                    BalloonManager.bolls[n] = 0
                if i.time > i.kill_time:
                    BalloonManager.bolls[n] = 0
                    Game.remove_object(i)

        if BalloonManager.time > BalloonManager.spawn_time:
            lst = [i for i, z in enumerate(BalloonManager.bolls) if z == 0]
            if len(lst) > 0:
                i = choice(lst)
                BalloonManager.bolls[i] = Balloon()
                BalloonManager.bolls[i].transform.xy = BalloonManager.poloj[i]
                Game.add_object(BalloonManager.bolls[i])
            BalloonManager.spawn_time = BalloonManager.time + 10


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
            self.spd.x = -abs(self.spd.x) if self.transform.x > self.x_lim[1] - v.x / 2 else abs(self.spd.x)
        if self.transform.y > self.y_lim[1] - v.y / 2 or self.transform.y < self.y_lim[0] + v.y / 2:
            self.spd.y = -abs(self.spd.y) if self.transform.y > self.y_lim[1] - v.y / 2 else abs(self.spd.y)


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
        self.crystal_count = 0

        self.massa = 1
        self.max_spd = 250
        self.spd = Vector(0, 0)
        self.accel = [1000, 250]
        self.G = 900
        self.fric = [0.87, 1]
        self.jump_spd = 500
        self.max_spd_para = 80

        self.myhat = None

        self.para = Sprite("ira_sprites/krila.png")
        self.para.transform.set_parent(self)
        self.para.transform.xy = 0, 0
        self.para.visible = False

        self.zg = Sprite("ira_sprites/morg.png")
        self.zg.transform.set_parent(self)
        self.zg.transform.xy = 0, 0
        self.zg.visible = False
        self.vm = self.time + randint(1, 4)

        self.transform.xy = Game.ширинаЭкрана // 2, Game.высотаЭкрана * 2 // 3
        # self.transform.scale_xy = 2, 2
        self.def_parent = None

    def got_crystal(self):
        self.crystal_count += 1

    def on_enter_game(self):
        Game.add_object(self.para)
        self.para.change_order(-1)
        Game.add_object(self.zg)

    def on_leave_game(self):
        Game.remove_object(self.zg)
        Game.remove_object(self.para)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.zg.visible = self.time > self.vm and self.time < self.vm + 0.2

        if not self.zg.visible and self.time > self.vm:
            self.vm = self.time + randint(1, 4)

        inair = 0 if self.is_grounded() else 1

        dx = Input.get("Horizontal" + self.igr)

        if Input.get("Jump" + self.igr) and not inair:

            if self.crystal_count>=1 and self.transform.x>872 and self.transform.x<1013 and self.transform.y>672:


                    if self.myhat:
                        if self.myhat.time < 1:
                            return 
                        else:
                            Game.remove_object(self.myhat)

                    h=Hat(randint(0,2))
                    Game.add_object(h)
                    h.transform.set_parent(self)
                    self.crystal_count-=1
                    self.myhat=h

            else:
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

            elev = 2

            if self.spd.y >= 0:
                pl = list(Game.get_objects(clas=Plat))
                cc = self.get_collided(pl, test_offset=Vector(0, elev + 3))

                if len(cc) > 0:
                    r = True
                    clue = True
                    self.spd.y = 0

                    pl = [cc[0][0]]

                    vy = 5
                    while len(self.get_collided(pl, test_offset=Vector(0, vy + elev))) > 0:
                        vy -= 1

                    self.transform.y = self.transform.y + vy

                    if self.transform.parent != pl[0]:
                        self.transform.set_parent(pl[0], True)

        if self.transform.parent and not clue:
            self.transform.detach(True)
            if self.def_parent:
                self.transform.set_parent(self.def_parent, True)

        return r


    def draw(self, dest: pygame.Surface):
        super().draw(dest)

        if self.crystal_count>0:

            a = Game.font.render(str(self.crystal_count), True, (0, 0, 0))
            tr = self.transform.get_world_transform()
            dest.blit(a, (tr.pos.x, tr.pos.y - self.get_size().y/2 * tr.scale_y -16) )


class Camera(GameObject):
    def update(self, deltaTime: float):
        super().update(deltaTime)

        Game.debug_str = str(pygame.mouse.get_pos())
        # if self.focus:
        #     wt=self.focus.transform.to_local_coord(self.transform,Vector(0),False)
        #     self.transform.xy = -wt.x + Game.ширинаЭкрана//2,-wt.y+Game.высотаЭкрана//2


Game.before_update(BalloonManager.add_ball)
Game.before_update(CrystalManager.add_crystal)

root = Camera()
Game.add_object(root)

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
    plat1.transform.set_parent(root)

ob = Plat("ira_sprites/oback.png")
ob.collision_image = pygame.image.load("ira_sprites/ocollider.png").convert_alpha()
ob.transform.xy = 120, 150
ob.spd = Vector(70, 0)
ob.transform.scale_xy = 7, 6
ob.x_lim = [0, Game.ширинаЭкрана - 250]
Game.add_object(ob)
ob.transform.set_parent(root)

girl1 = Base('1')
Game.add_object(girl1)
girl1.transform.scale_xy = 1, 1
girl1.transform.set_parent(root)
girl1.def_parent = root

girl = Base('2')
Game.add_object(girl)
girl.transform.scale_xy = 0.8, 0.8



stat = Totem()
Game.add_object(stat)
stat.transform.scale_xy = 2, 2
stat.transform.xy = 797, 692

girl.transform.set_parent(root)
girl.def_parent = root

root.focus = girl

hays = Sprite("ira_sprites/hays.png")
Game.add_object(hays)
hays.transform.xy = Game.ширинаЭкрана - hays.get_size().x, Game.высотаЭкрана - hays.get_size().y
hays.transform.scale_xy = 2, 2
hays.transform.set_parent(root)

obf = Sprite("ira_sprites/ofront.png")
obf.transform.set_parent(ob)
Game.add_object(obf)

# uni = Unicorn()
# uni.transform.xy=100,100
# uni.owner = girl
# Game.add_object(uni)
#
# uni = Unicorn()
# uni.transform.xy=200,100
# uni.owner = girl1
# Game.add_object(uni)

Game.run()
