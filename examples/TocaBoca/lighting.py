import pygame

from interier import Interier
from ramka import GameObject, Game, Cooldown


class LightEmitter:
    pass


class LightItem(LightEmitter, Interier):
    pass


class Lighting(GameObject):
    applied_light = 1

    def __init__(self):
        super().__init__()

        self.parent_sort_me_by = "     "

        self.light_map = pygame.Surface(Game.размерЭкрана, flags=pygame.SRCALPHA)
        self.light_map.fill((0, 0, 0, 200))

        self.update_cd = Cooldown(0.15)

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.update_cd.ready:
            self.update_cd.start()
            lights = 0
            for l in Game.get_objects(clas=LightEmitter, filter=lambda l: l.visible and (l.state.id == 1)):
                lights += 1
                break

            Lighting.applied_light = lights

    def draw(self, dest: pygame.Surface):
        if not Lighting.applied_light:
            dest.blit(self.light_map, (0, 0))
