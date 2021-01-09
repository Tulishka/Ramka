from typing import Dict, Union, List

import pygame
from .gameobject import GameObject
from .input import Input
from .layers import Layer



class Game:
    pygame.init()
    defaultLayer = Layer("default", 0)
    showFPS = True
    font = pygame.font.SysFont("arial", 14)
    gameObjects: List[GameObject] = []
    экран: pygame.Surface
    ширинаЭкрана, высотаЭкрана = размерЭкрана = (1024, 768)
    цветФона: pygame.Color = (0, 0, 20)
    clock = pygame.time.Clock()
    debug_str = ''
    drawOptions = {}

    layers: List[Layer] = [defaultLayer]

    @staticmethod
    def get_layer(name: str) -> Layer:
        l = list(filter(lambda x: x.name == name, Game.layers))
        if len(l) == 0:
            raise LookupError(f"Слой с именем '{name}' не найден!")
        return l[0]

    @staticmethod
    def add_layer(name: str, order: float) -> Layer:
        if len(list(filter(lambda x: x.name == name, Game.layers))) > 0:
            raise LookupError(f"Слой с именем '{name}' уже есть!")
        layer = Layer(name, order)
        Game.layers.append(layer)
        Game.sort_layers()
        return layer

    @staticmethod
    def sort_layers():
        Game.layers = sorted(Game.layers, key=lambda x: x.order)

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
    def add_object(game_object: GameObject, layer: Union[str, Layer, None] = None):
        if game_object not in Game.gameObjects:
            Game.gameObjects.append(game_object)

        if layer is None:
            layer = Game.defaultLayer

        if type(layer) == str:
            layer = Game.get_layer(layer)

        game_object.set_layer(layer)

    @staticmethod
    def remove_object(game_object: GameObject):
        if game_object in Game.gameObjects:
            game_object.set_layer(None)
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

            Input.update(deltaTime)
            Game.новый_кадр()

            for l in Game.layers:
                for obj in l.gameObjects:
                    if obj.enabled:
                        obj.update(deltaTime)
                        if obj.visible:
                            obj.draw(Game.экран, Game.drawOptions)

            # for obj in Game.gameObjects:
            #     if obj.enabled:
            #         obj.update(deltaTime)
            #         if obj.visible:
            #             obj.draw(Game.экран, Game.drawOptions)

            if Game.showFPS:
                ss=str(round(Game.clock.get_fps())) +", "+Game.debug_str+", " + Input.info()
                a =Game.font.render( ss , 1, (255, 255, 100))
                Game.экран.blit(a, (5, 5))

            Game.закончить_кадр()
