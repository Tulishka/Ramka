from typing import Dict, Union

import pygame


class Game:
    showFPS = True
    from .gameobject import GameObject

    font = pygame.font.SysFont("arial", 14)

    def __init__(self, caption: str, fullscreen: bool = False, window_size=None,
                 back_color: pygame.color.Color = (0, 0, 20)):
        self.размерЭкрана = (800, 600) if not fullscreen else pygame.display.list_modes()[0]

        if not window_size is None:
            self.размерЭкрана = window_size

        self.экран = pygame.display.set_mode(size=self.размерЭкрана,
                                             flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.HWACCEL | (
                                                 0 if not fullscreen else pygame.FULLSCREEN))
        pygame.display.set_caption(caption)

        self.ширинаЭкрана, self.высотаЭкрана = self.размерЭкрана

        self.цвет_фона = back_color
        self.clock = pygame.time.Clock()

        self.gameObjects: Dict[str, Game.GameObject] = {}

    def add_object(self, name: str, game_object: GameObject, parent: GameObject = None):
        game_object.game = self
        if parent is None:
            if name in self.gameObjects:
                self.remove_object(name)
            self.gameObjects[name] = game_object
        else:
            parent.add_child(name, game_object)

    def remove_object(self, game_object: Union[str, GameObject]):
        if type(game_object) == str:
            if game_object in self.gameObjects:
                ob = self.gameObjects[game_object]
                del self.gameObjects[game_object]
                ob.game = None
                ob.remove()
        else:
            idx = [n for n, x in self.gameObjects.items() if x == game_object]
            if len(idx):
                del self.gameObjects[idx[0]]
                game_object.game = None
                game_object.remove()

    def deltaTime(self):
        return self.clock.get_time() * 0.001

    def новый_кадр(self):
        self.экран.fill(self.цвет_фона)

    def закончить_кадр(self):
        pygame.display.flip()
        self.clock.tick(60)

    def __iter__(self):
        for name, obj in self.gameObjects.items():
            yield (name, obj)
            for name_c, obj_c in obj:
                yield (name_c, obj_c)

    def run(self):
        while 1:

            deltaTime = self.deltaTime()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    exit()

            self.новый_кадр()

            for name, obj in self:
                if obj.enabled:
                    obj.update(deltaTime)
                    if obj.visible:
                        obj.draw(self.экран, {"show_offset": 0})

            if Game.showFPS:
                a = Game.font.render(str(round(self.clock.get_fps())), 1, (255, 255, 100))
                self.экран.blit(a, (5, 5))

            self.закончить_кадр()
