import pygame

from ramka import Sprite, Game


class InvCell:
    def __init__(self, obj, cnt):
        self.obj = obj
        self.cnt = cnt


class Inventar(Sprite):
    item_images = {
        0: "ira_sprites/rost.png",
        1: "ira_sprites/steavphen.png",
        2: "ira_sprites/steavmyka.png",
        3: "ira_sprites/steavxleb.png",
        4: "ira_sprites/steavugalok.png",
        5: "ira_sprites/steavizum.png",
    }

    keys = {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6}

    def __init__(self, size=6):
        super().__init__("ira_sprites/steavinventar.png")
        self.cells = [None for _ in range(size)]
        self.width = self.get_size().x / size

    def set_cell(self, n, obj, cnt):
        if self.cells[n]:
            Game.remove_object(self.cells[n].obj)
        c = InvCell(obj, cnt)
        self.cells[n] = c
        obj.transform.set_parent(self.transform)
        Game.add_object(obj, layer=Game.uiLayer)
        obj.transform.y = 0
        obj.transform.x = self.width * (n - 2.5)

    def inc_count(self, n, d=1):
        if self.cells[n]:
            self.cells[n].cnt += d

    def dec_count(self, n, d=1):
        if self.cells[n]:
            self.cells[n].cnt -= d
            if self.cells[n].cnt < 0:
                self.cells[n].cnt = 0

    def get_count(self, n):
        if self.cells[n]:
            return self.cells[n].cnt
        else:
            return 0

    def update(self, deltaTime: float):
        super().update(deltaTime)

    def draw(self, dest: pygame.Surface):
        super().draw(dest)
        y = round(self.transform.y + self.width / 4)
        x = round(self.transform.x - 2.25 * self.width)
        for n, c in enumerate(self.cells):
            if c:
                a = Game.font.render(str(c.cnt), True, (255, 255, 255))
                dest.blit(a, (round(x + n * self.width), y))

    def get_item_image(self, n):
        return self.cells[n].obj.curr_animation().get_image(self.cells[n].obj.time)