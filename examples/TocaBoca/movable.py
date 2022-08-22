from examples.Components.DragAndDrop import Draggable
from examples.TocaBoca.base_item import BaseItem, DropZone
from examples.TocaBoca.base_item_components import FallingDown
from ramka import Input, Game, Vector
from ramka.effects import Effects
from ramka.gameobject_animators import PosAnimator


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
        return dz.can_attach_object(self)

    def is_attached(self):
        return isinstance(self.get_parent(), DropZone)

    def attach_to(self, dz: DropZone):
        if not self.is_attached():
            self.__restore_parent = self.get_parent()
            if dz.attach_object(self):
                # self.transform.pos = 0, 0
                PosAnimator(self, Vector(0, 0), 0.2)().kill()
                self.on_attach(dz)

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
                    self.transform.set_parent(self.__restore_parent, from_world=True)
                    self.__restore_parent = None
                self.on_detach(dz)

    def on_attach(self, dz):
        self.__fallcomp.enabled = False

    def on_detach(self, dz):
        self.__fallcomp.enabled = True

    def on_drag_end(self):
        if self.is_attachable():
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