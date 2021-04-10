from typing import Dict, List, Tuple

from .shared import *

FlipStyle = Tuple[bool, bool]


class Animation:
    def __init__(self, images: List[pygame.Surface], fps: int, looped: bool):
        self.images = images
        self.fps = fps
        self.looped = looped
        self.events = []

    def get_image(self, time: float) -> pygame.Surface:
        return self.images[self.get_frame_index(time)]

    def get_frame_index(self, time: float) -> int:
        if self.looped:
            return int(self.fps * time) % len(self.images)
        else:
            return min(int(self.fps * time) , len(self.images)-1)


def slice_image(image: pygame.Surface, size: (int, int) = None, cols: int = None, rows: int = None, row: int = 0) -> [
    pygame.Surface]:
    if size is None:
        rows = 1 if rows is None else rows
        cols = (image.get_width() // (image.get_height() // rows)) if cols is None else cols
        size = (image.get_width() // cols, image.get_height() // rows)

    return [image.subsurface(pygame.Rect((x * size[0], row * size[1]), size)) for x in range(cols)]


def generate_flip(images: List[pygame.Surface], flip_style: FlipStyle) -> Dict[FlipStyle, List]:
    res = {(False, False): images}

    if flip_style[0]:
        res[(True, False)] = [pygame.transform.flip(img, True, False) for img in images]
        if flip_style[1]:
            res[(True, True)] = [pygame.transform.flip(img, True, True) for img in images]

    if flip_style[1]:
        res[(False, True)] = [pygame.transform.flip(img, False, True) for img in images]

    return res
