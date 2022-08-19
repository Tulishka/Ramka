import random

import pygame

from examples.Components.mini_map import MiniMapItem
from examples.ferma2.Kust import Kust
from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Fly_item import Fly_item
from examples.ferma2.Inventar import Inventar
from examples.ferma2.Kost import Kost
from ramka import Sprite, Animation, Cooldown, Game, Input, Vector


class Igrok(MiniMapItem,Sprite):
    def ani(self):
        return {
        "idle": Animation("ira_sprites/steav.png", 5, True),
        "walk": Animation("ira_sprites/stiavgo?.png", 5, True),
        "drop": Animation("ira_sprites/steavdrop.png", 5, True),
    }
    MAX_COUNT = 10

    def __init__(self):
        super().__init__(self.ani())
        self.spd = 300
        self.inv = Inventar()
        self.inv.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана - self.inv.get_size().y / 2
        self.anim_cd = Cooldown(0.25)

    def on_enter_game(self):
        Game.add_object(self.inv, layer=Game.uiLayer)
        for n, i in Inventar.item_images.items():
            self.inv.set_cell(n, Sprite(i), 20 if n > 0 else Igrok.MAX_COUNT)

    def update(self, deltaTime: float):
        super().update(deltaTime)
        dx = Input.get("Horizontal")
        self.transform.pos = self.transform.pos + self.spd * Vector(dx, Input.get("Vertical")) * deltaTime
        if self.anim_cd.ready:
            self.state.animation = "walk" if dx else "idle"
        if dx:
            self.transform.scale_x = abs(self.transform.scale_x) * (-1 if dx < 0 else 1)
        kust = list(Game.get_objects(clas=Kust))
        ekust = False
        if len(kust) > 0:
            cc = self.get_collided(kust)
            for c, f in cc:
                ekust = True
                break

        if pygame.K_SPACE in Game.keys_pressed and self.inv.get_count(0) > 0 and not ekust:
            self.inv.dec_count(0, 1)
            kust = Kust()
            Game.add_object(kust)
            kust.transform.pos = self.transform.pos

        if pygame.K_f in Game.keys_pressed:
            wp=Input.mouse_pos-self.screen_pos()
            kost = Kost(self.transform.pos+wp)
            if len(list(Game.get_objects(clas=Kost))) == 0:
                Game.add_object(kost)
                kost.transform.pos = self.transform.pos

        if pygame.K_e in Game.keys_pressed:
            kust = list(
                Game.get_objects(clas=Kust, filter=lambda k: k.state.animation == "rezult" and self.is_collided(k)))
            if len(kust) > 0:
                kust = kust[0]
                self.state.animation = "drop"
                self.anim_cd.start()
                kust.harvest()

            avt = list(Game.get_objects(clas=Avtomat, filter=lambda k: self.is_collided(k)))
            if len(avt) > 0:
                self.state.animation = "drop"
                self.anim_cd.start()
                avt = avt[0]
                run = True
                for rt in avt.get_resources_types():
                    run = False
                    if self.inv.get_count(rt) > 0:
                        if avt.can_accept_res(rt):
                            self.inv.dec_count(rt)

                            def dol(item):
                                if not avt.add_res(item.n):
                                    self.inv.inc_count(item.n)
                                Game.remove_object(item)

                            r = Fly_item(Inventar.item_images[rt], avt, dol)
                            r.n = rt
                            r.transform.pos = self.transform.pos + Vector(random.randint(10, 30), 0).rotate(
                                random.randint(30, 330))
                            Game.add_object(r)
                if run:
                    avt.try_start()

        kosti = list(Game.get_objects(clas=Kost, filter=lambda k: k.ready and self.is_collided(k)))
        if len(kosti) > 0:
            kost = kosti[0]
            Game.remove_object(kost)

        itm = Game.get_objects(clas=Fly_item, filter=lambda k: k.pickable() and self.is_collided(k))
        for i in itm:
            self.inv.inc_count(i.pick_type, 1)
            Game.remove_object(i)

        nki = Inventar.keys.intersection(Game.keys_pressed)
        for k in nki:
            t = k - pygame.K_1

            if self.inv.get_count(t) > 0:
                kf = self.transform.pos + Vector(0, 50).rotate(random.randint(-70, 70))

                def col(it):
                    it.pick_type = t

                fl = Fly_item(Inventar.item_images[t], kf, col)
                fl.transform.pos = self.transform.pos
                Game.add_object(fl)
                self.inv.dec_count(t)
                break