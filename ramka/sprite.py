import math
from typing import Dict

from .gameobject import GameObject

from .animation import Animation, FlipStyle
from .shared import *



class Sprite(GameObject):

    def __init__(self, animations: Dict[str, Animation]):
        super().__init__()
        self.animations = animations
        self.last_animation = None
        self.image_offset = Vector(0.0)
        self.image_rotate_offset = 0

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

        wtr = self.transform.get_world_transform()
        flp = self.get_flip()
        img = self.curr_animation().get_frame(self.time, (flp[0] ^ (wtr._scale.x < 0), flp[1] ^ (wtr._scale.y < 0)))

        sx = abs(wtr._scale.x)
        sy = abs(wtr._scale.y)

        if sx != 1 or sy != 1:
            img = pygame.transform.scale(img, (int(img.get_width() * sx), int(img.get_height() * sy)))

        rotate_image= wtr._angle + self.image_rotate_offset
        if rotate_image != 0:
            img = pygame.transform.rotate(img, rotate_image)

        rotated_offset = self.image_offset if wtr._angle == 0 else self.image_offset.rotate(-wtr._angle)
        if self.image_offset and (wtr._scale.x != 1 or wtr._scale.y != 1) :
            rotated_offset = rotated_offset * wtr._scale.elementwise()

        rect = img.get_rect(center=wtr._pos - rotated_offset)

        dest.blit(img, rect)  # , special_flags=pygame.BLEND_ALPHA_SDL2

        if options.get("show_box") == True:
            pygame.draw.rect(dest, (255, 100, 100), rect, 2)

        if options.get("show_offset") == True:
            pygame.draw.circle(dest, (255, 100, 100), wtr._pos, 2)
