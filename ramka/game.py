from typing import Dict, Union, List, Callable, Iterable
import pygame
import pymunk
import pymunk.pygame_util

from . import Vector
from .timers import Timers
from .gameobject import GameObject
from .input import Input
from .layers import Layer


class ObjectFilter:
    def __init__(self, clas: Union[type, Iterable[type]] = None, layer: Layer = None, filter: Callable = None):
        self.clas = clas
        self.layer = layer
        self.filter = filter

    def __call__(self, *args, **kwargs) -> Iterable[GameObject]:
        return Game.get_objects(self.clas, self.layer, self.filter)


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

    layers: List[Layer] = [defaultLayer, uiLayer]

    ph_space = pymunk.Space()
    ph_gravity = (0.0, 900.0)
    ph_draw_options: pymunk.pygame_util.DrawOptions

    point_sprite = pygame.sprite.Sprite()

    point_sprite.rect = pygame.Rect(0, 0, 0, 0)
    point_sprite.image = pygame.Surface((2, 2))
    pygame.draw.rect(point_sprite.image, (255, 255, 255), pygame.Rect(0, 0, 2, 2), 0)
    point_sprite.mask = pygame.mask.from_surface(point_sprite.image)

    time = 0

    mouse_capture = None
    lock_input = None

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

        Game.размерЭкрана = Game.экран.get_size()
        Game.screen_size = Vector(Game.размерЭкрана)

        Game.ширинаЭкрана, Game.высотаЭкрана = Game.размерЭкрана

        Game.ph_draw_options = pymunk.pygame_util.DrawOptions(Game.экран)

        if back_color is not None:
            Game.цветФона = back_color

    @staticmethod
    def _notify_event_listeners(game_object, event_type, notified_object: GameObject = None,
                                check_parent_recursively=False):
        if not notified_object:
            objs = Game.get_objects(filter=lambda x: x.event_listeners)
        else:
            objs = [notified_object]
        ls = []

        if check_parent_recursively and notified_object:

            objs = game_object.get_all_parents()

            def enum(o: GameObject) -> Iterable[Callable]:
                for z in o.event_listeners:
                    if z.type == event_type:
                        if getattr(z, "recursively", False) or o is notified_object:
                            yield z

            get_listeners = enum

        else:
            get_listeners = lambda o: filter(lambda z: z.type == event_type, o.event_listeners)

        for o in objs:
            ls.extend(get_listeners(o))

        for l in ls:
            if (l.clas is None or isinstance(game_object, l.clas)) and (
                    l.layer is None or game_object.layer == l.layer) and (l.filter(game_object) if l.filter else True):
                l(game_object)

    @staticmethod
    def add_object(game_object: GameObject, layer: Union[str, Layer, None] = None):
        if game_object not in Game.gameObjects:

            if not layer:
                layer = game_object.requested_layer_name

            if type(layer) == str and layer:
                layer = Game.get_layer(layer)

            if not layer:
                layer = Game.defaultLayer

            game_object.set_layer(layer)
            Game._notify_event_listeners(game_object, "other_enter_game")
            Game.rearrange_gobjects()
            game_object.on_enter_game()

    @staticmethod
    def remove_object(game_object: GameObject):
        game_object.visible = False
        game_object.enabled = False

        if game_object not in Game.gameObjects:
            return

        for c in game_object.transform.children.copy():
            Game.remove_object(c.gameObject)

        game_object.on_leave_game()
        game_object.set_layer(None)
        Game._notify_event_listeners(game_object, "other_leave_game")

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
    def rearrange_gobjects():
        Game.gameObjects = [obj for l in Game.layers for obj in l.gameObjects]

    @staticmethod
    def run():

        skip_time = 2

        while 1:

            if skip_time:
                deltaTime = 0
                skip_time -= 1
            else:
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

            Game.rearrange_gobjects()
            gobs = Game.gameObjects.copy()

            for ul in Game.before_update_listeners:
                ul(deltaTime)

            for obj in gobs:
                if obj.enabled:
                    obj.update(deltaTime)
                    obj.update_components(deltaTime)

            Game.mouse_capture = None
            Game.break_event_loop = False
            if Game.lock_input:
                if Game.lock_input not in Game.gameObjects or not Game.lock_input.enabled:
                    Game.lock_input = None
                    inpl = reversed(gobs)
                else:
                    inpl = [Game.lock_input]
            else:
                inpl = reversed(gobs)
            for obj in inpl:
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
                        elif ev.type == "hover":
                            if (
                                    Game.mouse_capture is None or Game.mouse_capture == obj) and obj.is_visible() and obj.opacity and obj.touch_test(
                                Input.mouse_pos):
                                if Game.mouse_capture is None:
                                    Game.mouse_capture = obj
                                cap = ev()
                                if isinstance(cap, GameObject):
                                    Game.mouse_capture = cap

                        elif ev.type == "mouse_down":
                            bs = mbtn if ev.continuos else Game.mouse_pressed
                            if bs:
                                if ev.hover:
                                    r = (
                                                Game.mouse_capture is None or Game.mouse_capture == obj) and obj.is_visible() and obj.opacity and obj.touch_test(
                                        Input.mouse_pos)
                                    if r and Game.mouse_capture is None:
                                        Game.mouse_capture = obj
                                else:
                                    r = True
                                if r and (ev.button is None or ev.button in bs):
                                    if ev.button is not None:
                                        cap = ev()
                                    else:
                                        cap = ev(bs)
                                    if ev.hover and isinstance(cap, GameObject):
                                        Game.mouse_capture = cap

                        elif ev.type == "mouse_up":
                            if Game.mouse_released:
                                if ev.hover:
                                    r = (
                                                Game.mouse_capture is None or Game.mouse_capture == obj) and obj.is_visible() and obj.opacity and obj.touch_test(
                                        Input.mouse_pos)
                                    if r and Game.mouse_capture is None:
                                        Game.mouse_capture = obj
                                else:
                                    r = True
                                if r and (ev.button is None or ev.button in Game.mouse_released):
                                    if ev.button is not None:
                                        cap = ev()
                                    else:
                                        cap = ev(Game.mouse_released)
                                    if ev.hover and isinstance(cap, GameObject):
                                        Game.mouse_capture = cap
                if Game.lock_input or Game.break_event_loop:
                    break

            for ul in Game.after_update_listeners:
                ul(deltaTime)

            for dl in Game.before_draw_listeners:
                dl(Game.экран)

            for obj in gobs:
                if obj.is_visible():
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
    def get_object(clas: Union[type, Iterable[type]] = None, layer: Layer = None, filter: Callable = None,
                   revers=False):
        if filter is None:
            filter = lambda x: True

        if revers:
            objs = reversed(Game.gameObjects)
        else:
            objs = Game.gameObjects

        if not isinstance(clas, Iterable):
            for c in objs:
                if (clas is None or isinstance(c, clas)) and (layer is None or c.layer == layer) and filter(c):
                    return c
        else:
            for c in objs:
                if (not clas or any(
                        isinstance(c, t) for t in clas)) and (layer is None or c.layer == layer) and filter(c):
                    return c

    @staticmethod
    def get_objects(clas: Union[type, Iterable[type]] = None, layer: Layer = None, filter: Callable = None,
                    revers=False):
        if filter is None:
            filter = lambda x: True

        if revers:
            objs = reversed(Game.gameObjects)
        else:
            objs = Game.gameObjects

        if not isinstance(clas, Iterable):
            for c in objs:
                if (clas is None or isinstance(c, clas)) and (layer is None or c.layer == layer) and filter(c):
                    yield c
        else:
            for c in objs:
                if (not clas or any(
                        isinstance(c, t) for t in clas)) and (layer is None or c.layer == layer) and filter(c):
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
    def on_hover(func):
        func.event_descriptor = 1
        func.type = "hover"
        return func

    @staticmethod
    def on_mouse_up(func=None, *, button=None, hover=True):

        def wrapper(func):
            func.event_descriptor = 1
            func.button = button
            func.type = "mouse_up"
            func.hover = hover
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_child_add(func=None, *, recursively=False, clas=None, layer=None, filter=None):
        def wrapper(func):
            func.event_descriptor = 2
            func.clas = clas
            func.layer = layer
            func.filter = filter
            func.recursively = recursively
            func.type = "on_child_add"
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_child_remove(func=None, *, recursively=False, clas=None, layer=None, filter=None):
        def wrapper(func):
            func.event_descriptor = 2
            func.clas = clas
            func.layer = layer
            func.filter = filter
            func.recursively = recursively
            func.type = "on_child_remove"
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def on_message(func=None, *, name=None, sender=None):
        def wrapper(func):
            func.event_descriptor = 3
            func.name = name
            func.sender = sender
            func.type = "on_message"
            return func

        return wrapper if func is None else wrapper(func)

    @staticmethod
    def break_input_eventloop():
        Game.break_event_loop = True
