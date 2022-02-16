import math
from typing import Dict, Callable, Union, Tuple

from .gameobject import GameObject

from .animation import Animation, FlipStyle, slice_image
from .shared import *
from .transformbase import TransformBase


class Sprite(GameObject):

    def __init__(self, animations: Union[Animation, pygame.Surface, str, Dict[str, Animation]], duration=None, slice_images_rows=1, slice_images_cols=1):
        super().__init__()

        if type(animations) == str:
            if "*" in animations or "?" in animations:
                import glob
                files=list(glob.glob(animations))
                files.sort()
                animations = Animation([pygame.image.load(f).convert_alpha() for f in files], round(len(files) / (duration if duration else 0.5)), True)
            else:
                animations=pygame.image.load(animations).convert_alpha()

        if type(animations)==pygame.Surface and (slice_images_rows>1 or slice_images_cols>1):
            cnt=slice_images_rows * slice_images_cols
            animations = Animation(slice_image(animations, cols=slice_images_cols,rows=slice_images_rows), round(cnt / (duration if duration else 0.5)), True)

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
        self.collision_image_transformable = True
        self.collider_cache_image = None

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
        img = self.curr_animation().get_image(self.time)
        return Vector(img.get_size())

    def get_rect(self):
        if self.sprite.rect.size[0] == 0:
            self.prepare_image()
        return self.sprite.rect

    def get_image_transformed(self, img: pygame.Surface, flip: FlipStyle, scale: (float, float) = (1.0, 1.0),
                              rotate:  float= 0.0) -> pygame.Surface:

        flip = (flip[0] ^ (scale[0] < 0), flip[1] ^ (scale[1] < 0))

        sx = abs(scale[0])
        sy = abs(scale[1])

        w = int(img.get_width() * sx)
        h = int(img.get_height() * sy)

        if w<1:
            w=1

        if h<1:
            h=1


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
                self.cache = {hsh: ci}

        return ci

    def prepare_mask(self):
        """ Required actual self.sprite.image at autogen mode! \n
            Требуется актуальное значение self.sprite.image если режим автосоздание маски включен!
         """
        if self.collision_image:
            if self.collision_image_transformable:
                wtr = self.transform.get_world_transform()
                flp = self.get_flip()
                rotate_image = wtr._angle + self.image_rotate_offset

                img = self.get_image_transformed(self.collision_image, flp, (wtr._scale.x, wtr._scale.y), rotate_image)
            else:
                img=self.collision_image
        else:
            img=self.sprite.image

        self.sprite.mask = pygame.mask.from_surface(img)
        self.collider_cache_image = img

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
        if self.opacity:
            # self.sprite.image.set_alpha(int(min(max(self.opacity, 0), 1.0) * 255))
            dest.blit(self.sprite.image, self.sprite.rect)  # , special_flags=pygame.BLEND_ALPHA_SDL2
            # if self.collider_cache_image:
            #     dest.blit(self.collider_cache_image, self.sprite.rect)  # , special_flags=pygame.BLEND_ALPHA_SDL2

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
        po = pos - self.get_rotated_offset(p) - p._pos
        return self.local_to_image_pos(po)

