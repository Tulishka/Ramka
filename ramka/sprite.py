import math
from typing import Dict, Callable

from .gameobject import GameObject

from .animation import Animation, FlipStyle
from .shared import *
from .transformbase import TransformBase


class Sprite(GameObject):

    def __init__(self, animations: Dict[str, Animation]):
        super().__init__()
        self.animations = animations
        self.last_animation = None
        self.image_offset = Vector(0.0)
        self.image_rotate_offset = 0
        self.sprite = pygame.sprite.Sprite()
        self.sprite.rect = Rect(0, 0, 0, 0)
        self.sprite.image = None
        self.sprite.mask = None
        self.cache = {}
        self.deep_cache = False


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

    def get_size(self) -> Vector:
        idx, img = self.curr_animation().get_image(self.time, (False, False))
        return Vector(img.get_size())

    def get_rect(self):
        if self.sprite.rect.size[0] == 0:
            self.prepare_image()
        return self.sprite.rect

    def get_image_transformed(self, time: float, flip: FlipStyle, scale: (float, float) = (1.0, 1.0),
                              rotate: float = 0.0) -> pygame.Surface:

        flip = (flip[0] ^ (scale[0] < 0), flip[1] ^ (scale[1] < 0))
        img = self.curr_animation().get_image(time, flip)

        sx = abs(scale[0])
        sy = abs(scale[1])

        w = int(img.get_width() * sx)
        h = int(img.get_height() * sy)

        rotate = round(rotate * 10) * 0.1

        if abs(rotate) > 360:
            rotate = rotate - int(rotate / 360) * 360

        hsh = (img, flip, w, h, rotate)

        ci = self.cache.get(hsh)
        if ci is None:
            ci = img
            if scale[0] != 1 or scale[1] != 1:
                ci = pygame.transform.scale(ci, (w, h))

            if rotate != 0:
                ci = pygame.transform.rotate(ci, rotate)

            if self.deep_cache:
                self.cache[hsh] = ci
            else:
                self.cache = {hash:ci}

        return ci


    def prepare_mask(self):
        self.sprite.mask = pygame.mask.from_surface(self.sprite.image)

    def prepare_image(self):
        wtr = self.transform.get_world_transform()
        flp = self.get_flip()

        rotate_image = wtr._angle + self.image_rotate_offset

        img = self.get_image_transformed(self.time, flp, (wtr._scale.x, wtr._scale.y), rotate_image)

        if img!=self.sprite.image:
            self.sprite.image = img
            self.prepare_mask()

        rotated_offset = self.get_rotated_offset(wtr)
        self.sprite.rect = self.sprite.image.get_rect(center=wtr._pos + rotated_offset)



    def draw(self, dest: pygame.Surface):

        self.prepare_image()
        dest.blit(self.sprite.image, self.sprite.rect)  # , special_flags=pygame.BLEND_ALPHA_SDL2

    def draw_overlay(self, dest: pygame.Surface):
        super().draw_overlay(dest)

        wtr = self.transform.get_world_transform()
        pygame.draw.circle(dest, (255, 100, 100), wtr._pos, 2)

    def get_rotated_offset(self, wtr: TransformBase):

        rotated_offset = self.image_offset if wtr._angle == 0 else self.image_offset.rotate(-wtr._angle)
        if self.image_offset and (wtr._scale.x != 1 or wtr._scale.y != 1):
            rotated_offset = rotated_offset * wtr._scale.elementwise()

        return -rotated_offset

    def is_collided(self, other: GameObject,func: Callable = None) -> bool:
        if func is None:
            func=pygame.sprite.collide_mask
        if isinstance(other, Sprite) and self.sprite.image is not None and other.sprite.image is not None:
            return other.visible and func(self.sprite, other.sprite)
        else:
            return super().is_collided(other)

