from typing import Dict, Union, List
import pygame
import pymunk
import pymunk.pygame_util

from .collider import Collider
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

    before_update_listeners = []
    after_update_listeners = []
    before_draw_listeners = []
    after_draw_listeners = []

    layers: List[Layer] = [defaultLayer]

    ph_space = pymunk.Space()
    ph_gravity = (0.0, 900.0)
    ph_draw_options: pymunk.pygame_util.DrawOptions

    point_sprite = pygame.sprite.Sprite()

    point_sprite.rect = pygame.Rect(0, 0, 0, 0)
    point_sprite.image = pygame.Surface((2, 2))
    pygame.draw.rect(point_sprite.image, (255, 255, 255), pygame.Rect(0,0,2,2), 0)
    point_sprite.mask = pygame.mask.from_surface(point_sprite.image)

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

        Game.ph_draw_options = pymunk.pygame_util.DrawOptions(Game.экран)

        if back_color is not None:
            Game.цветФона = back_color

    @staticmethod
    def add_object(game_object: GameObject, layer: Union[str, Layer, None] = None):
        if layer is None:
            layer = Game.defaultLayer
        if type(layer) == str:
            layer = Game.get_layer(layer)
        game_object.set_layer(layer)

        if game_object not in Game.gameObjects:
            Game.gameObjects.append(game_object)
            game_object.on_enter_game()

    @staticmethod
    def remove_object(game_object: GameObject):
        if game_object in Game.gameObjects:
            game_object.on_leave_game()
            game_object.set_layer(None)
            Game.gameObjects.remove(game_object)

    @staticmethod
    def deltaTime():
        return Game.clock.get_time() * 0.001

    @staticmethod
    def frame_begin():
        Game.экран.fill(Game.цветФона)

    @staticmethod
    def frame_end():
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
            Game.frame_begin()

            for ul in Game.before_update_listeners:
                ul(deltaTime)

            for l in Game.layers:
                for obj in l.gameObjects:
                    if obj.enabled:
                        obj.update_components(deltaTime)
                        obj.update(deltaTime)
                        for c in obj.get_components(Collider):
                            c.color = (255, 0, 0) if c.get_collided(Game.get_components(Collider)) is not None else (
                                0, 255, 0)

            for ul in Game.after_update_listeners:
                ul(deltaTime)

            for dl in Game.before_draw_listeners:
                dl(Game.экран)

            for l in Game.layers:
                for obj in l.gameObjects:
                    if obj.visible:
                        obj.draw(Game.экран)
                        obj.draw_components(Game.экран)

            for dl in Game.after_draw_listeners:
                dl(Game.экран)

            # Game.ph_space.step(deltaTime)

            if Game.showFPS:
                ss = str(round(Game.clock.get_fps())) + ", " + Game.debug_str  # + ", " + Input.info()
                a = Game.font.render(ss, True, (255, 255, 100))
                Game.экран.blit(a, (5, 5))

            Game.frame_end()

    @staticmethod
    def get_components(component_class=None):
        for c in Game.gameObjects:
            for cc in c.get_components(component_class):
                yield cc

    @staticmethod
    def get_objects(clas=None, layer=None, filter=None):
        if filter is None:
            filter = lambda x: True

        for c in Game.gameObjects:
            if (clas is None or isinstance(c, clas)) and (layer is None or c.layer == layer) and filter(c):
                yield c

    @staticmethod
    def before_update(update_func):
        Game.before_update_listeners.append(update_func)
        return update_func

    @staticmethod
    def after_update(update_func):
        Game.after_update_listeners.append(update_func)
        return update_func

    @staticmethod
    def after_draw(draw_func):
        Game.after_draw_listeners.append(draw_func)
        return draw_func

    @staticmethod
    def before_draw(draw_func):
        Game.before_draw_listeners.append(draw_func)
        return draw_func
