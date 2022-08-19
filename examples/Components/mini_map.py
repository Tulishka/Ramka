import pygame

from ramka import GameObject, Game


class MiniMapItem:
    def get_color(self):
        return (100, 100, 100)

    def get_radius(self):
        return 2


class MiniMap(GameObject):
    def __init__(self):
        super().__init__()
        self.radius = 70
        self.scale = self.radius * 2 / Game.ширинаЭкрана
        self.transform.pos = self.radius + 16, self.radius + 16

    def draw(self, dest: pygame.Surface):
        cmm = self.screen_pos()
        pygame.draw.circle(dest, (230, 230, 230), cmm, self.radius)
        obj = Game.get_objects(clas=MiniMapItem)
        dbr = self.radius * self.radius
        ce = Game.screen_size * 0.5

        for i in obj:
            r = i.get_radius()
            cv = i.get_color()
            p = (i.screen_pos() - ce) * self.scale
            if p.length_squared() > dbr:
                p.scale_to_length(self.radius - r)
            p = cmm + p
            pygame.draw.circle(dest, cv, p, r)
