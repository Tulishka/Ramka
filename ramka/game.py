from typing import Dict, Union, List

import pygame
from .gameobject import GameObject


class Game:
    showFPS = True
    font = pygame.font.SysFont("arial", 14)
    gameObjects: List[GameObject] = []
    экран: pygame.Surface
    ширинаЭкрана, высотаЭкрана = размерЭкрана = (1024, 768)
    цветФона: pygame.Color = (0, 0, 20)
    clock = pygame.time.Clock()
    counter=0
    drawOptions = {}

    @staticmethod
    def init(caption: str, back_color: pygame.Color = None, fullscreen: bool = False, window_size=None):

        Game.размерЭкрана = (1024, 768) if not fullscreen else pygame.display.list_modes()[0]

        if not window_size is None:
            Game.размерЭкрана = window_size

        Game.экран = pygame.display.set_mode(size=Game.размерЭкрана,
                                             flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.HWACCEL | (
                                                 0 if not fullscreen else pygame.FULLSCREEN))
        pygame.display.set_caption(caption)

        Game.ширинаЭкрана, Game.высотаЭкрана = Game.размерЭкрана

        if back_color is not None:
            Game.цветФона = back_color

    @staticmethod
    def add_object(game_object: GameObject):
        if game_object not in Game.gameObjects:
            Game.gameObjects.append(game_object)

    @staticmethod
    def remove_object(game_object: GameObject):
        if game_object in Game.gameObjects:
            Game.gameObjects.remove(game_object)

    @staticmethod
    def deltaTime():
        return Game.clock.get_time() * 0.001

    @staticmethod
    def новый_кадр():
        Game.экран.fill(Game.цветФона)

    @staticmethod
    def закончить_кадр():
        pygame.display.flip()
        Game.clock.tick(60)

    @staticmethod
    def run():
        while 1:

            deltaTime = Game.deltaTime()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    exit()

            Game.новый_кадр()

            for obj in Game.gameObjects:
                if obj.enabled:
                    obj.update(deltaTime)
                    if obj.visible:
                        obj.draw(Game.экран, Game.drawOptions)

            if Game.showFPS:
                a = Game.font.render(str(round(Game.clock.get_fps()))+" ,"+str(Game.counter), 1, (255, 255, 100))
                Game.экран.blit(a, (5, 5))

            Game.закончить_кадр()
