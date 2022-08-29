from base_item import DropZone
from base_item_components import ParentJockey
from nav_bar import NavBar
from movable import Movable
from ramka import Game


class Creature(Movable):
    def __init__(self, *a, **b):

        super().__init__(*a, **b)
        self.creature_bar_order = "1"

    def on_attach(self, dz):
        super().on_attach(dz)
        if dz.trigger_name == "Saddle":
            self.timers.set_timeout(0.5, lambda x: ParentJockey(self))

    def on_detach(self, dz):
        super().on_detach(dz)
        for i in self.get_components(component_class=ParentJockey):
            i.remove()

    def on_enter_game(self):
        super().on_enter_game()
        nav = Game.get_object(clas=NavBar, filter=lambda n: n.name == "creature_select")
        if nav:
            nav.add_btn(self, self.creature_bar_order)

    def on_leave_game(self):
        super().on_leave_game()
        nav = Game.get_object(clas=NavBar, filter=lambda n: n.name == "creature_select")
        if nav:
            nav.remove_btn(self)

    def get_default_pretty_points(self):
        res = super().get_default_pretty_points()
        res.update({'seat': (0, self.get_size()[1] * 0.25)})
        return res

    def init_from_dict(self, d):
        super().init_from_dict(d)
        p = self.get_parent()
        if isinstance(p, DropZone) and p.trigger_name == "Saddle":
            self.timers.set_timeout(0.5, lambda x: ParentJockey(self))
