from chelik_nav import NavBar
from movable import Movable
from ramka import Game


class Creature(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.creature_bar_order="1"

    def on_enter_game(self):
        super().on_enter_game()
        nav = Game.get_object(clas=NavBar, filter=lambda n: n.name == "creature_select")
        if nav:
            nav.add_btn(self, self.creature_bar_order)
