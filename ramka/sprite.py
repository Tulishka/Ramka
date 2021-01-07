import math
from typing import Dict

from .rotationstyles import RotationFree
from .gameobject import GameObject

from .animation import Animation, FlipStyle
from .shared import *
from .state import State, state_default


class Sprite(GameObject):

    def __init__(self, animations: Dict[str, Animation],
                 state: State = state_default):
        super().__init__()
        self.animations = animations
        self.state = state
        self.last_animation = None
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

        wtr = self.transform.get_world_transform()
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
