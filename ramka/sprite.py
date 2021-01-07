import math
from typing import Dict

from .animation import Animation, FlipStyle
from .gameobject import GameObject
from .shared import *
from .state import State, state_default
from .transform import Transform


class RotationStyle:

    def transform_ip(self, transform: Transform) -> Transform:
        return transform

    def transform(self, transform: Transform) -> Transform:
        return self.transform_ip(transform.copy())


class RotationNone(RotationStyle):
    def transform_ip(self, transform: Transform):
        transform.rotate = 0
        transform.scale.xy = abs(transform.scale.x),abs(transform.scale.y)
        return transform


class RotationFree(RotationStyle):
    def __init__(self, discrete: int = 0):
        super().__init__()
        self.discrete = discrete

    def transform_ip(self, transform: Transform) -> Transform:
        transform.rotate = transform.rotate if self.discrete == 0 else ((round(
            transform.rotate) + (self.discrete >> 1)) // self.discrete) * self.discrete
        return transform


class RotationFlip(RotationStyle):
    def __init__(self, flip_style: FlipStyle):
        super().__init__()
        self.flip_style = flip_style

    def transform_ip(self, transform: Transform) -> Transform:
        v = Vector(1.0, 0.0)
        v.rotate_ip(transform.rotate)
        if self.flip_style[0] and v.x < 0:
            transform.scale.x = -transform.scale.x
        if self.flip_style[1] and v.y < 0:
            transform.scale.y = -transform.scale.y

        transform.rotate = 0
        return transform


class RotationTarget(RotationStyle):
    def __init__(self, pos: Vector, shift=0.0):
        super().__init__()
        self.pos = pos
        self.shift = shift

    def transform_ip(self, transform: Transform) -> Transform:
        angle = -Vector(1.0, 0.0).angle_to(self.pos - transform.pos)
        transform.rotate = angle + self.shift
        return transform


class RotationCopy(RotationStyle) :
    def __init__(self, target: Transform):
        super().__init__()
        self.target = target

    def transform_ip(self, transform: Transform) -> Transform:
        transform.rotate = self.target.rotate
        transform.scale = Vector(math.copysign(transform.scale.x, self.target.scale.x),
                                 math.copysign(transform.scale.y, self.target.scale.y))
        return transform


class Sprite(GameObject):

    def __init__(self, animations: Dict[str, Animation], transform: Transform = None,
                 state: State = state_default):
        super().__init__(transform)
        self.animations = animations
        self.state = state
        self.last_animation = None
        self.transform = transform if not transform is None else Transform()
        self.transform.modifier_func = RotationFree(2).transform

    def curr_animation(self):
        ani = self.animations.get(self.state.animation)
        if ani is None:
            if self.last_animation is None:
                ani = next(iter(self.animations.values()))
            else:
                ani = self.last_animation

        self.last_animation = ani
        return ani

    def get_flip(self) -> FlipStyle:
        return (False, False)

    def draw(self, dest: pygame.Surface, options: Dict[str, any] = {}):

        wtr = self.get_world_transform()
        flp = self.get_flip()
        img = self.curr_animation().get_frame(self.time, (flp[0] ^ (wtr.scale.x < 0), flp[1] ^ (wtr.scale.y < 0)))

        sx=abs(wtr.scale.x)
        sy=abs(wtr.scale.y)

        if sx != 1 or sy != 1:
            img = pygame.transform.scale(img, (int(img.get_width() * sx), int(img.get_height() * sy)))

        if wtr.rotate != 0:
            img = pygame.transform.rotate(img, wtr.rotate)

        rotated_offset = wtr.offset if wtr.rotate == 0 else wtr.offset.rotate(-wtr.rotate)
        rect = img.get_rect(center=wtr.pos - rotated_offset)

        dest.blit(img, rect)  # , special_flags=pygame.BLEND_ALPHA_SDL2

        if options.get("show_box") == True:
            pygame.draw.rect(dest, (255, 100, 100), rect, 2)

        if options.get("show_offset") == True:
            pygame.draw.circle(dest, (255, 100, 100), wtr.pos, 2)
