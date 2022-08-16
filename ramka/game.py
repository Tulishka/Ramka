from typing import Dict, Union, List
import pygame
import pymunk
import pymunk.pygame_util

from . import Vector
from .timers import Timers
from .collider import Collider
from .gameobject import GameObject
from .input import Input
from .layers import Layer


class Game:
    key_press_listeners = []
    keys_pressed = set([])
    mouse_pressed = set([])
    pygame.init()
    defaultLayer = Layer("default", 0)
    uiLayer = Layer("ui", 999)
    showFPS = True
    font = pygame.font.SysFont("arial", 14)
    gameObjects: List[GameObject] = []
    экран: pygame.Surface
    ширинаЭкрана, высотаЭкрана = размерЭкрана = (1024, 768)
    screen_size = Vector(ширинаЭкрана, высотаЭкрана)
    цветФона: pygame.Color = (0, 0, 20)
    clock = pygame.time.Clock()
    debug_str = ''
    drawOptions = {}

    before_update_listeners = []
    after_update_listeners = []
    before_draw_listeners = []
    after_draw_listeners = []

    layers: List[Layer] = [defaultLayer,uiLayer]

    ph_space = pymunk.Space()
    ph_gravity = (0.0, 900.0)
    ph_draw_options: pymunk.pygame_util.DrawOptions

    point_sprite = pygame.sprite.Sprite()

    point_sprite.rect = pygame.Rect(0, 0, 0, 0)
    point_sprite.image = pygame.Surface((2, 2))
    pygame.draw.rect(point_sprite.image, (255, 255, 255), pygame.Rect(0, 0, 2, 2), 0)
    point_sprite.mask = pygame.mask.from_surface(point_sprite.image)

    time = 0

    timers = Timers()

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
    def _notify_enter_leave_listeners(game_object, event_type):
        objs = Game.get_objects(filter=lambda x: x.event_listeners)
        ls = []
        for o in objs:
            ls.extend(filter(lambda z: z.type == event_type, o.event_listeners))

        for l in ls:
            if (l.clas is None or isinstance(game_object, l.clas)) and (
                    l.layer is None or game_object.layer == l.layer) and (l.filter(game_object) if l.filter else True):
                l(game_object)

    @staticmethod
    def add_object(game_object: GameObject, layer: Union[str, Layer, None] = None):
        if layer is None:
            layer = Game.defaultLayer
        if type(layer) == str:
            layer = Game.get_layer(layer)
        game_object.set_layer(layer)

        if game_object not in Game.gameObjects:
            Game._notify_enter_leave_listeners(game_object, "other_enter_game")

            Game.gameObjects.append(game_object)
            game_object.on_enter_game()

    @staticmethod
    def remove_object(game_object: GameObject):
        if game_object in Game.gameObjects:
            game_object.on_leave_game()
            game_object.set_layer(None)
            Game.gameObjects.remove(game_object)
            Game._notify_enter_leave_listeners(game_object, "other_leave_game")

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
            Game.time += deltaTime
            Game.keys_pressed = set()
            Game.mouse_pressed = set()
            Game.mouse_released = set()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    exit()
                else:
                    if (event.type == pygame.KEYDOWN):
                        Game.keys_pressed.add(event.key)
                        for li in Game.key_press_listeners:
                            li(event.key)
                    elif (event.type == pygame.MOUSEBUTTONDOWN):
                        Game.mouse_pressed.add(event.button)
                    elif (event.type == pygame.MOUSEBUTTONUP):
                        Game.mouse_released.add(event.button)

            Input.update(deltaTime)
            Game.frame_begin()

            Game.timers.update(deltaTime)

            keys = [i + 1 for i, j in enumerate(Input.raw_keys) if j]
            mbtn = [i + 1 for i, j in enumerate(Input.raw_mouse_buttons) if j]

            for ul in Game.before_update_listeners:
                ul(deltaTime)

            for l in Game.layers:
                for obj in l.gameObjects:
                    if obj.enabled:
                        for ev in obj.event_listeners:
                            if ev.event_descriptor != 1:
                                continue
                            if ev.type == "key_down":
                                ks = keys if ev.continuos else Game.keys_pressed
                                if ks:
                                    if not ev.key or ev.key in ks:
                                        if ev.key is not None:
                                            ev()
                                        else:
                                            ev(ks)
                            elif ev.type == "mouse_down":
                                bs = mbtn if ev.continuos else Game.mouse_pressed
                                if bs:
                                    if ev.hover:
                                        r = obj.touch_test(Input.mouse_pos)
                                    else:
                                        r = True
                                    if r and (ev.button is None or ev.button in bs):
                                        if ev.button is not None:
                                            ev()
                                        else:
                                            ev(bs)
                            elif ev.type == "mouse_up":
                                if Game.mouse_released:
                                    if ev.hover:
                                        r = obj.touch_test(Input.mouse_pos)
                                    else:
                                        r = True
                                    if r and (ev.button is None or ev.button in Game.mouse_released):
                                        if ev.button is not None:
                                            ev()
                                        else:
                                            ev(Game.mouse_released)

                        obj.update_components(deltaTime)
                        obj.update(deltaTime)

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

    @staticmethod
    def on_key_down(func=None, *, key=None, continuos=False):

        def wrapper(func):
            func.event_descriptor = 1
            func.key = key
            func.type = "key_down"
            func.continuos = continuos
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_other_enter_game(func=None, *, clas=None, layer=None, filter=None):
        def wrapper(func):
            func.event_descriptor = 2
            func.clas = clas
            func.layer = layer
            func.filter = filter
            func.type = "other_enter_game"
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_other_leave_game(func=None, *, clas=None, layer=None, filter=None):
        def wrapper(func):
            func.event_descriptor = 2
            func.clas = clas
            func.layer = layer
            func.filter = filter
            func.type = "other_leave_game"
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_mouse_down(func=None, *, button=None, continuos=False, hover=True):

        def wrapper(func):
            func.event_descriptor = 1
            func.button = button
            func.type = "mouse_down"
            func.continuos = continuos
            func.hover = hover
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_mouse_up(func=None, *, button=None, hover=True):

        def wrapper(func):
            func.event_descriptor = 1
            func.button = button
            func.type = "mouse_up"
            func.hover = hover
            return func

        return wrapper if func is None else wrapper(func)
