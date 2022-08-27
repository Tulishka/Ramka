from movable import Movable
from ramka import Input


class Transport(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.direction = 1
        self.last_pos = None

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.last_pos and self.is_dragged():
            delta = self.screen_pos().x - self.last_pos.x

            if delta > 1:
                self.direction = -1
            elif delta < -1:
                self.direction = 1

            self.transform.scale_x = self.direction

        self.last_pos = self.screen_pos()
