from base_item import BaseItem
from camera_pos import CameraPos
from ramka import Sprite, Game, Camera, GameObject, Vector
from ramka.effects import Effects


class NavBtn(Sprite):
    def __init__(self, anim, chelik):
        super().__init__(anim)
        self.chelik = chelik
        self.eff = Effects(self)

    @Game.on_mouse_down(button=1)
    def on_mouse_down(self):
        self.eff.pulse(duration=0.2)

        def tap(t):
            self.chelik.eff.pulse(duration=0.5, koef=1.05)

        if isinstance(Camera.main.target, CameraPos):
            Camera.main.target.animate_to(self.chelik, tap)


class NavBar(GameObject):

    def __init__(self):
        super().__init__()
        self.transform.pos = Vector(50, 50)
        self.btns_gap = 10
        Game.add_object(self, Game.uiLayer)

    def add_btn(self, object: BaseItem, prefix:str=""):
        for i in self.get_children(filter=lambda x: x.chelik == object):
            return
        nb = NavBtn(object.create_item_icon(), object)
        nb.parent_sort_me_by=str(prefix)+nb.parent_sort_me_by
        nb.transform.set_parent(self)
        Game.add_object(nb, self.layer)
        self.rearrange()

    def remove_btn(self, object: BaseItem):
        for i in self.get_children(filter=lambda x: x.chelik == object):
            i.transform.set_parent(None)
            Game.remove_object(i)
            self.rearrange()
            return

    def rearrange(self):
        self.layer.sort_object_children(self)
        pos = Vector(0)
        for i in self.get_children():
            i.transform.pos = pos
            pos.x += i.get_computed_size().x + self.btns_gap
