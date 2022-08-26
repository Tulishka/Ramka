import math

import pygame

from examples.Components.DragAndDrop import Draggable
from base_item import BaseItem, DropZone
from base_item_components import FallingDown
from ramka import Input, Game, Vector, GameObject
from ramka.effects import Effects


class Movable(Draggable, BaseItem):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.__fallcomp = FallingDown(self)

        self.last_position = self.transform.pos
        self.last_vert_spd = 0
        self.eff = Effects(self)

        self.__restore_parent = None

    def on_drag_start(self):
        self.detach()
        self.eff.pulse(1.1, 0.5)

    def is_attachable(self):
        return True

    def can_attach_to(self, dz: DropZone):
        return self.is_attachable() and dz.can_attach_object(self)

    def is_attached(self):
        return isinstance(self.get_parent(), DropZone)

    def attach_to(self, dz: DropZone):
        if not self.is_attached():
            self.__restore_parent = self.get_parent()
            if dz.attach_object(self):
                self.on_attach(dz)

    def __resolv_restore_parent(self):
        if callable(self.__restore_parent):
            self.__restore_parent = self.__restore_parent()

    def detach(self):
        if self.is_attached():
            dz = self.get_parent()

            if isinstance(dz, DropZone):
                res = dz.detach_object(self)
            else:
                res = True
                self.transform.detach(True)

            if res:
                if self.__restore_parent:
                    self.__resolv_restore_parent()
                    if self.__restore_parent:
                        self.transform.set_parent(self.__restore_parent, from_world=True)
                    self.__restore_parent = None
                self.on_detach(dz)

    def on_attach(self, dz):
        self.__fallcomp.enabled = False

    def on_detach(self, dz):
        self.__fallcomp.enabled = True

    def on_drag_end(self):
        if not self.is_attached() and self.is_attachable():
            ll = list(Game.get_objects(clas=DropZone, filter=lambda x: self not in x.get_all_parents()))
            for dz in reversed(ll):
                if dz.is_collided(self) or dz.is_collided(Input.mouse_pos):
                    if self.can_attach_to(dz):
                        self.attach_to(dz)
                        return

        if self.last_vert_spd < 0:
            self.__fallcomp.spd = max(self.last_vert_spd / self.mass, -600)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.is_dragged() and deltaTime > 0:
            self.last_vert_spd = (self.transform.pos.y - self.last_position.y) / deltaTime
        else:
            self.last_vert_spd = 0

        self.last_position = self.transform.pos

    def get_init_dict(self):
        res = super().get_init_dict()
        self.__resolv_restore_parent()
        res.update({
            "__fallcomp.enabled": self.__fallcomp.enabled,
            "__restore_parent": self.__restore_parent.uuid if self.__restore_parent and hasattr(self.__restore_parent,
                                                                                                "uuid") else None,
        })
        return res

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        # self.__fallcomp.enabled = opts.get("__fallcomp.enabled", False)
        self.__fallcomp.enabled = self.get_parent(clas=DropZone) is None
        n = opts.get("__restore_parent", False)
        if n and n != "null":
            self.__restore_parent = lambda: Game.get_object(filter=lambda x: getattr(x, "uuid", False) == n)

    def draw(self, dest: pygame.Surface):
        super().draw(dest)

        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            icn=self.get_icon()
            pos = self.screen_pos() - (icn.get_size()[0]/2, icn.get_size()[1] + self.get_size()[1]/2 ) - self.image_offset + Vector(0,3*math.sin(self.time*8))
            dest.blit(icn, dest=pygame.Rect(pos, Vector(0)))

