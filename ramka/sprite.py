import math
from typing import Dict, Callable, Union, Tuple

from .gameobject import GameObject

from .animation import Animation, FlipStyle
from .shared import *
from .transformbase import TransformBase


class Sprite(GameObject):

    def __init__(self, animations: Union[Animation, pygame.Surface, Dict[str, Animation]]):
        super().__init__()

        if type(animations) == pygame.Surface:
            animations = Animation([animations], 0, True)

        if type(animations) == Animation:
            animations = {"default": animations}

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
        self.collision_image = None

    def curr_animation(self):
        ani = self.animations.get(self.state.animation)
        if ani is None:
            if self.last_animation is None:
                ani = next(iter(self.animations.values()))
            else:
                ani = self.last_animation

        self.last_animation = ani
        return ani

    def get_size(self) -> Vector:
        idx, img = self.curr_animation().get_image(self.time)
        return Vector(img.get_size())

    def get_rect(self):
        if self.sprite.rect.size[0] == 0:
            self.prepare_image()
        return self.sprite.rect

    def get_image_transformed(self, img: pygame.Surface, flip: FlipStyle, scale: (float, float) = (1.0, 1.0),
                              rotate: float = 0.0) -> pygame.Surface:

        flip = (flip[0] ^ (scale[0] < 0), flip[1] ^ (scale[1] < 0))

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

            if flip[0] or flip[1]:
                ci = pygame.transform.flip(ci, flip[0], flip[1])

            if scale[0] != 1 or scale[1] != 1:
                ci = pygame.transform.scale(ci, (w, h))

            if rotate != 0:
                ci = pygame.transform.rotate(ci, rotate)

            if self.deep_cache:
                self.cache[hsh] = ci
            else:
                self.cache = {hash: ci}

        return ci

    def prepare_mask(self):
        """ Required actual self.sprite.image at autogen mode! \n
            Требуется актуальное значение self.sprite.image если режим автосоздание маски включен!
         """
        self.sprite.mask = pygame.mask.from_surface(self.sprite.image)

    def prepare_image(self):
        wtr = self.transform.get_world_transform()
        flp = self.get_flip()

        rotate_image = wtr._angle + self.image_rotate_offset

        img = self.curr_animation().get_image(self.time)
        img = self.get_image_transformed(img, flp, (wtr._scale.x, wtr._scale.y), rotate_image)

        if img != self.sprite.image:
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

    def is_collided(self, other: GameObject, func: Callable = None) -> Union[bool, Tuple[int, int]]:
        if func is None:
            func = pygame.sprite.collide_mask
        if other.visible and isinstance(other,
                                        Sprite) and self.sprite.image is not None and other.sprite.image is not None:
            return func(self.sprite, other.sprite)
        else:
            return super().is_collided(other)

    def move_rect(self, offset: Vector):
        self.sprite.rect.move_ip(offset)

    def image_pos_to_local(self, pos: Vector) -> Vector:
        r = self.get_rect()
        return Vector(pos.x - r.width // 2, pos.y - r.height // 2)

    def local_to_image_pos(self, pos: Vector) -> Vector:
        r = self.get_rect()
        return Vector(pos.x + r.width // 2, pos.y + r.height // 2)

    def image_pos_to_global(self, pos: Vector) -> Vector:
        p = self.transform.get_world_transform()
        return p._pos + self.get_rotated_offset(p) + self.image_pos_to_local(pos)

    def global_to_image_pos(self, pos: Vector) -> Vector:
        p = self.transform.get_world_transform()
        po = p.sub_from_vector(pos - self.get_rotated_offset(p))
        return self.local_to_image_pos(po)
