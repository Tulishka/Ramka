import pygame

from ramka import GameObject, Vector, Game, Input


class Selectable:
    pass

class SelectManager(GameObject):
    def __init__(self):
        super().__init__()
        self.selected = []
        self.pos_maus = None

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.pos_maus:
            self.selected=[]
            mi=Vector(min(self.pos_maus.x, Input.mouse_pos.x), min(self.pos_maus.y, Input.mouse_pos.y))
            ma=Vector(max(self.pos_maus.x, Input.mouse_pos.x), max(self.pos_maus.y, Input.mouse_pos.y))
            celiki_in_ramka = Game.get_objects(clas=Selectable)
            for i in celiki_in_ramka:
                if i.transform.pos.x > mi.x and i.transform.pos.x < ma.x and i.transform.pos.y > mi.y and i.transform.pos.y < ma.y:
                    self.selected.append(i)


        for i in self.selected:
            if i not in Game.gameObjects:
                self.selected.remove(i)

    def draw(self, dest: pygame.Surface):
        for i in self.selected:
            pygame.draw.rect(dest, (0, 255, 0), i.get_rect(), 3)
        if self.pos_maus:
            sz = Input.mouse_pos - self.pos_maus
            sz.x = abs(sz.x)
            sz.y = abs(sz.y)
            p = Vector(min(self.pos_maus.x, Input.mouse_pos.x), min(self.pos_maus.y, Input.mouse_pos.y))
            pygame.draw.rect(dest, (0, 255, 0), pygame.Rect(p, sz), 2)

    @Game.on_mouse_up(hover=False, button=1)
    def mouse_up(self):
        self.pos_maus = None

    @Game.on_mouse_down(hover=False, button=1)
    def find_new_friend(self):
        sel = Game.get_objects(clas=Selectable)
        for s in sel:
            if s.touch_test():
                self.select_item(s)
                return
        self.selected = []
        self.pos_maus = Input.mouse_pos

    def select_item(self, item):
        self.selected = [item]