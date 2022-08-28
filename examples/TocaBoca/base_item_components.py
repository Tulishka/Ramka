from random import randint

from examples.Components.DragAndDrop import Draggable
from ramka import Component, Sprite, Game, Cooldown


class FallingDown(Component):
    floor_y = 900

    def __init__(self, game_obj: Sprite):
        super().__init__(game_obj)

        self.spd = 0
        self.g = 900
        self.enabled = True

    @Game.on_mouse_down(button=3, hover=True)
    def mouse_3_click(self):
        self.spd = -max(800 / self.gameObject.mass, 400)

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if not self.enabled or isinstance(self.gameObject, Draggable) and self.gameObject.is_dragged():
            self.spd = 0
            return

        y = self.gameObject.screen_pos().y + self.gameObject.get_computed_size().y * 0.5
        if y < self.floor_y or self.spd < 0:
            self.spd += self.g * deltaTime
        elif self.spd > 0:
            if self.spd < 200:
                self.spd = 0
                # self.gameObject.transform.y = self.floor_y + 1 - self.gameObject.get_computed_size().y * 0.5

            else:
                self.spd *= -0.3
        if self.spd:
            self.gameObject.transform.y = self.gameObject.transform.y + self.spd * deltaTime

        if y > Game.высотаЭкрана - 10:
            self.gameObject.transform.y = Game.высотаЭкрана - 11 - self.gameObject.get_computed_size().y * 0.5


class ParentJockey(Component):

    def __init__(self, game_obj: Sprite):
        super().__init__(game_obj)

        self.spd = 0
        self.g = 900
        self.enabled = True
        self.parent_start_pos = None
        self.parent_last_pos = None

        self.host=None

    def on_add(self):
        self.host = self.gameObject.get_parent(clas=Sprite)
        if self.host is None:
            return
        self.parent_start_pos = self.host.transform.pos
        print("start jokeyed",self.host)

    def on_remove(self):
        print("end jokeyed")

    def update(self, deltaTime: float):
        super().update(deltaTime)

        p = self.host
        if p is None:
            return

        if self.parent_last_pos is None:
            self.parent_last_pos = p.transform.pos
            return

        dl = p.transform.pos - self.parent_last_pos

        self.gameObject.transform.pos = dl

        self.parent_last_pos = p.transform.pos


class Blink(Component):
    def __init__(self, obj):
        super().__init__(obj)
        self.blink = Cooldown(0.1)
        self.blink_time = 0

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if not self.blink.ready:
            self.gameObject.state.animation = "blink" + str(self.gameObject.state.id)

        if self.gameObject.time > self.blink_time:
            self.blink.start()
            self.blink_time = self.gameObject.time + randint(1, 8)
