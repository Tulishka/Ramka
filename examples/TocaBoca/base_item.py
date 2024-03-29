import glob

import pygame

from examples.Components.DragAndDrop import Draggable, DragAndDropController
from game_classes import GameClasses
from base_item_components import Blink
from iconable import Iconable
from savable import Savable
from typing import Dict, Union, Tuple, List, Iterable
from ramka import GameObject, Sprite, Game, Animation, Vector, Input
from ramka.gameobject_animators import PosAnimator
from ramka.trigger import Trigger


class BaseItem(Sprite):
    ...


class TriggerZone(Draggable, Savable, Trigger):
    def __init__(self, parent: BaseItem, name, pos: Vector = None, radius=None, parent_sort_order=None, **kwargs):
        super().__init__(name, pos, radius, parent, color=(255, 0, 0), **kwargs)

        if parent_sort_order:
            self.parent_sort_me_by = parent_sort_order

    @staticmethod
    def get_creation_params(dict, parent):
        return [], {
            "parent": parent,
            "name": dict["trigger_name"],
        }

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        self.radius = opts['radius']
        if 'poly' in opts:
            if opts['poly']:
                self.set_poly([Vector(t) for t in opts['poly']])

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "radius": self.radius,
            "trigger_name": self.trigger_name,
            "poly": [tuple(t) for t in self._poly] if self._poly else None,
        })
        return res

    @staticmethod
    def interactive():
        return pygame.key.get_mods() & pygame.KMOD_LCTRL

    def on_drag_start(self):
        return self.interactive()

    @Game.on_key_down
    def on_key_press(self, keys):
        if self.interactive() and self.touch_test(Input.mouse_pos):
            if 1073741911 in keys:
                self.radius += 10
            elif 1073741910 in keys:
                self.radius -= 10
                if self.radius < 20:
                    self.radius = 10

    def draw(self, dest: pygame.Surface):
        if self.interactive():
            super().draw(dest)


class DropZone(TriggerZone):
    attach_none = 0
    attach_point = 1
    attach_vertical = 2
    attach_horizontal = 3

    def __init__(self, parent: BaseItem, name, pos: Vector = None, radius=None, max_items=1,
                 accept_class: Iterable = [],
                 pretty_point="center", attach_style=1, floor_y=None, parent_sort_order=None, **kwargs):
        super().__init__(parent, name, pos, radius, parent_sort_order, **kwargs)
        self.max_items = max_items
        self.accept_class = accept_class
        self.attach_style = attach_style
        self.floor_y = floor_y

        if not isinstance(parent, BaseItem):
            raise Exception("PrettyPoint: parent must be BaseItem!")

        self.pretty_point = pretty_point

    def can_attach_object(self, object: GameObject):
        return self.visible and (self.trigger_name != "Pocket" or object.get_size()[0] < self.radius * 1.5) and self.max_items > len(
            self.transform.children) and (not self.accept_class or any(
            isinstance(object, t) for t in self.accept_class)) and self.get_parent().can_accept_dropzone_object(self,
                                                                                                                object)

    def is_childs_freezed(self):
        return self.floor_y is None

    def update_attached_object_pos(self, object: GameObject):
        pos = -object.get_pretty_point(self.pretty_point)

        if self.attach_style > 0:
            if self.attach_style == DropZone.attach_horizontal:
                pos.x = object.transform.pos.x
            elif self.attach_style == DropZone.attach_vertical:
                pos.y = object.transform.pos.y

            if object.transform.pos.length() > Game.ширинаЭкрана:
                object.transform.pos = pos
            else:
                PosAnimator(object, pos, 0.2)().kill()

    def attach_object(self, object: GameObject):
        object.transform.set_parent(self, True)
        self.layer.sort_object_children(self.get_parent())

        self.update_attached_object_pos(object)

        self.get_parent().on_object_attached(self, object)
        return True

    def detach_object(self, object: GameObject):
        object.transform.detach(True)
        self.get_parent().on_object_detached(self, object)
        return True

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        self.max_items = opts['max_items']
        self.accept_class = [GameClasses.get_class(t) for t in opts['accept_class']]
        self.pretty_point = opts.get("pretty_point", "center")
        self.attach_style = opts.get("attach_style", DropZone.attach_point)
        self.floor_y = opts.get("floor_y", None)

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "max_items": self.max_items,
            "accept_class": [t.__name__ for t in self.accept_class],
            "pretty_point": self.pretty_point,
            "floor_y": self.floor_y,
            "attach_style": self.attach_style
        })
        return res


class PrettyPoint(Draggable, Trigger):
    def __init__(self, parent: BaseItem, name, pos: Vector):
        super().__init__(name, pos, 10, parent, color=(0, 200, 0))

        if not isinstance(parent, BaseItem):
            raise Exception("PrettyPoint: parent must be BaseItem!")

        self.points_holder = parent
        self.last_pos = parent.get_pretty_point(self.trigger_name)

    @staticmethod
    def interactive():
        return pygame.key.get_mods() & pygame.KMOD_LCTRL

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if not self.interactive():
            Game.remove_object(self)
        elif self.last_pos != self.transform.pos:
            self.points_holder.set_pretty_point(self.trigger_name, tuple(self.transform.pos))
            self.last_pos = self.transform.pos

    def draw(self, dest: pygame.Surface):
        if self.interactive():
            super().draw(dest)


class FrontPart(Draggable, Sprite):
    def __init__(self, animations: Union[Animation, pygame.Surface, str, Dict[str, Animation]], parent: BaseItem):
        super().__init__(animations)
        self.transform.set_parent(parent)
        self.parent_sort_me_by = "__" + self.parent_sort_me_by

    @Game.on_mouse_down(hover=True)
    def mouse_down_proxy(self, btn):
        return self.get_parent()

    @Game.on_mouse_up(hover=True)
    def mouse_up_proxy(self, btn):
        return self.get_parent()

    def on_drag_start(self):
        p = self.get_parent()
        if isinstance(p, Draggable):
            bs = p.on_drag_start()
            return bs if isinstance(bs, GameObject) else self.get_parent() if bs != False else False
        else:
            return False


class BaseItem(Savable, Iconable, Sprite):
    dd_manager: DragAndDropController = None
    animation_cache = {}

    def __init__(self, anim: str, pos, mass=None):

        if not isinstance(anim, str):
            print(anim, pos)
            raise Exception("Анимация BaseItem может быть создана только из строки! Неверный тип anim! ")

        self.name = anim.split("|")[-1]

        if anim in BaseItem.animation_cache:
            animations = BaseItem.animation_cache[anim]
        else:
            animations = BaseItem.create_animation(anim)
            # BaseItem.animation_cache[anim] = animations

        self.anim_path = anim

        self.type_uid = (type(self).__name__ + "|" + self.anim_path if isinstance(self.anim_path, str) else
                         ("other|" if "|" not in self.name else "") + self.name).replace("|", "@")
        self.origin = ""

        super().__init__(animations)
        self.drop_zones = []
        self.state.id = 1
        self.transform.pos = pos
        self.mouse_start_point = None

        self.pretty_points = self.get_default_pretty_points()

        if not BaseItem.dd_manager:
            BaseItem.dd_manager = Game.get_object(clas=DragAndDropController)

        if mass:
            self.mass = mass
        else:
            self.update_mass()

        if "blink1" in self.animations:
            Blink(self)

        if "mask" in self.animations:
            self.collision_image = self.animations["mask"].get_image(0)

        self.front_object = None
        if isinstance(anim, str):
            front_anim = BaseItem.create_animation(anim, "_f")
            if front_anim:
                self.front_object = FrontPart(front_anim, self)

        self.on_state_change()

    def create_pretty_points_controls(self):
        if pygame.key.get_mods() & pygame.KMOD_LCTRL:
            for i in self.get_children(clas=PrettyPoint):
                return
            for pk, pp in self.pretty_points.items():
                Game.add_object(PrettyPoint(self, pk, Vector(pp)))

    def set_pretty_point(self, name, pos) -> BaseItem:
        self.pretty_points[name] = pos if isinstance(pos, tuple) else tuple(pos)
        return self

    def set_pretty_points(self, points: Dict[str, Tuple]) -> BaseItem:
        self.pretty_points.update(points)
        return self

    def get_pretty_point(self, name, world_coord=False, obj_coord: GameObject = None) -> Vector:

        def transform(p):
            if world_coord:
                p = self.w_transform().add_to_vector(p)
            elif obj_coord:
                p = self.transform.to_local_coord(obj_coord.transform, p, False)
            else:
                p = self.transform.add_to_vector(p) - self.transform.pos
            return p

        if name.startswith("@"):
            comp = 0

            def min_v(val, v):
                if val is None or v[comp] < val[comp]:
                    val = v
                return val

            def max_v(val, v):
                if val is None or v[comp] > val[comp]:
                    val = v
                return val

            ff = name[1:].split("_")
            reducer = min_v if ff[0] == "min" else max_v
            comp = 0 if ff[1] == "x" else 1

            res = None
            for p in (Vector(p) for k, p in self.pretty_points.items() if k in ['top', 'bottom', 'left', 'right']):
                p = transform(p)
                res = reducer(res, p)

            p = res
        else:
            p = transform(Vector(self.pretty_points.get(name, (0, 0))))

        return p

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "anim_path": self.anim_path,
            "state.id": self.state.id,
            "mass": self.mass,
            "name": self.name,
            "pretty_points": self.pretty_points
        })
        return res

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        old = self.state.id
        self.state.id = opts["state.id"]
        self.mass = opts["mass"]
        self.name = opts.get("name", self.name)
        self.pretty_points.update(opts.get("pretty_points", {}))
        self.on_state_change(old)

    @staticmethod
    def get_creation_params(dict, parent):
        return [], {
            "anim": dict["anim_path"],
            "pos": Vector(dict["transform"]["x"], dict["transform"]["y"]),
        }

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return obj.get_size().x < self.get_size().x

    def on_object_attached(self, dz: DropZone, object: Sprite):
        pass

    def on_object_detached(self, dz: DropZone, object: Sprite):
        pass

    @staticmethod
    def create_animation(name, suffix=""):
        a = name.split("|")
        directory = a[-2]
        name = a[-1]
        obj = {}
        files = list(glob.glob(f".\\img\\{directory}\\{name}{suffix}??.png"))
        if files:
            files.sort()
            for f in files:
                if f[-5] == "m":
                    if f[-6].isdigit():
                        i = f[-6]
                    else:
                        i = '1'
                    obj["blink" + i] = Animation(f, 5, True)
                elif f[-5].isdigit():
                    obj[f"state{f[-5]}"] = Animation(f, 5, True)
                elif f[-5] == "i":
                    obj["mask"] = Animation(f, 5, True)
        elif not suffix:
            obj["default"] = Animation(f".\\img\\{directory}\\{name}.png", 5, True)
        return obj

    def drop_zone_add(self, name, pos: Vector = None, radius=35, max_items=1, accept_class=[],
                      pretty_point="center", attach_style=1, floor_y=None, parent_sort_order=None,
                      **kwargs) -> BaseItem:
        DropZone(self, name, pos, radius, max_items, accept_class, pretty_point, attach_style, floor_y,
                 parent_sort_order, **kwargs)
        return self

    def on_state_change(self, old=None):
        pass

    def state_next(self):
        old = self.state.id
        n = f"state{self.state.id + 1}"
        if n in self.animations:
            self.state.id += 1
        else:
            self.state.id = 1

        self.on_state_change(old)

    def state_anim_name(self):
        return f"state{self.state.id}"

    @Game.on_mouse_up(button=1)
    def on_mouse_up(self):
        if self.mouse_start_point:
            self.state_next()

    @Game.on_mouse_down
    def on_mouse_down(self, buttons):
        self.mouse_start_point = Input.mouse_pos

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.mouse_start_point:
            if (Input.mouse_pos - self.mouse_start_point).length_squared() > 30:
                self.mouse_start_point = None

        self.state.animation = self.state_anim_name()
        if self.front_object:
            self.front_object.state.animation = self.state.animation

        self.create_pretty_points_controls()

    def update_mass(self):
        sq = self.get_size()
        self.mass = sq.x * sq.y / (100 * 100)
        if self.mass < 1:
            self.mass = 1
        return self.mass

    def get_default_pretty_points(self):
        sz = self.get_size() * 0.5
        return {
            "center": (0, 0),
            "left": (-sz.x, 0),
            "right": (sz.x, 0),
            "bottom": (0, sz.y),
            "top": (0, -sz.y),
        }
