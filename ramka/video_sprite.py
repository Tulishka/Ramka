from typing import Callable, Tuple

from ramka import Sprite
from ramka.video import Video


class VideoSprite(Sprite):
    def __init__(self, filename, size: Tuple[int, int] = None, fps=None, speed=1, looped=True,
                 callback: Callable = None):
        self.video = Video(filename, size=size, fps=fps, speed=speed, looped=looped, callback=callback)
        super().__init__(self.video)

    def update(self, deltaTime: float):
        super().update(deltaTime)
        self.video.update(deltaTime)
