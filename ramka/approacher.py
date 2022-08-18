from typing import Union, Iterable, Tuple

import pygame

from . import GameObject, Game
from .transformbase import TransformBase
from .component import Component
from .shared import Vector


class Approacher(Component):

    def __init__(self, game_oject: Component.GameObject):
        from .transform import Transform
        super().__init__(game_oject)
        self.target = None
        self.max_speed = 0
        self.acceleration = 0
        self.deceleration = 0
        self.max_distance = 0
        self.min_distance = 0
        self.ignore_distance = 0
        self.ignore_zone_deceleration = 0
        self.speed = Vector(0, 0)
        self.x_direction = 1

    def approach(self, target: Union[Vector, GameObject], max_speed=200, acceleration=0, deceleration=0,
                 initial_speed: Vector = Vector(0, 0), max_distance=0,
                 min_distance=0, ignore_distance=0, start_pos=None, ignore_zone_deceleration=0):
        self.target = target
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.deceleration = acceleration if not deceleration else deceleration
        self.max_distance = max_distance
        self.min_distance = min_distance
        self.ignore_distance = ignore_distance if ignore_distance else 3 if acceleration else 0
        self.ignore_zone_deceleration = ignore_zone_deceleration if ignore_zone_deceleration else self.deceleration * 0.5
        self.speed = initial_speed
        if start_pos:
            self.gameObject.transform.pos = start_pos

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.target:
            if self.acceleration:

                transform = self.gameObject.transform

                if isinstance(self.target, GameObject):
                    dest = transform.to_parent_local_coord(self.target.transform)
                else:
                    dest = self.target

                dif = dest - transform.pos
                dst = dif.length_squared()
                spd = self.speed.length()

                if dst < self.ignore_distance * self.ignore_distance:
                    dp = Vector(0)
                    dece = self.ignore_zone_deceleration
                else:
                    dece = self.deceleration

                    stop_time = spd / dece
                    stop_dist = spd * stop_time + dece * (stop_time ** 2) / 2

                    if dst > stop_dist * stop_dist:
                        dif.scale_to_length(self.acceleration)
                        dp = dif
                    else:
                        dp = Vector(0)

                if dp.x and spd > 10:
                    self.x_direction = 1 if self.speed.x >= 0 else -1

                if dp.length_squared() < 0.1 and spd > 0:
                    if spd > 0.5:
                        dp = -self.speed
                        dp.scale_to_length(min(2 * spd, dece))
                    else:
                        dp = -self.speed * 0.5

                self.speed += dp * deltaTime

                if self.speed.length_squared() > self.max_speed * self.max_speed:
                    self.speed.scale_to_length(self.max_speed)

                transform.pos += self.speed * deltaTime

            else:
                self.gameObject.transform.move_toward_ip(self.target, self.max_speed * deltaTime,
                                                         ignore_distance=self.ignore_distance,
                                                         min_distance=self.min_distance, max_distance=self.max_distance)
