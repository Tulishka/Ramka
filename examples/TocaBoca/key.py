import pygame.sprite

from base_item import DropZone
from handable_item import HandableItem
from ramka import Game
from ramka.gameobject_animators import AngleAnimator


class Key(HandableItem):

    def __init__(self, *a, **b):
        super().__init__(*a, **b)

        self.angle_animator = None

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.is_dragged():
            obj = Game.get_object(clas=DropZone, filter=lambda x: x.trigger_name == "Head" and x.is_collided(self))
            if obj:
                angle = -90
            else:
                angle = 0

            if self.transform.angle != angle:
                if self.angle_animator and self.angle_animator.ready():
                    self.angle_animator.remove()
                    self.angle_animator = None

                if self.angle_animator is None:
                    def rem(tl):
                        self.angle_animator = None

                    self.angle_animator = AngleAnimator(self, angle, 0.1)().do(rem).kill()
