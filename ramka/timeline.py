from functools import reduce
from typing import Callable

from ramka import Component


class Timeline:
    ...


class TimeEvent:
    def __init__(self, start_time, action, duration, continuous=False):
        self.start_time = start_time
        self.action = action
        self.duration = duration
        self.continuous = continuous


class TimeLineProgressInfo:
    def __init__(self):
        self.timeline = None
        self.entire_progress = 0
        self.section_progress = 0
        self.entire_time = 0
        self.section_time = 0
        self.deltaTime = 0


class Timeline(Component):
    def __init__(self, game_object, tag=""):
        super().__init__(game_object, tag=tag)

        self.plan = []
        self.start_time = game_object.time
        self.fired_time = -1
        self.__paused_progress = None

    def duration(self):
        if self.plan:
            return max(x.start_time + x.duration for x in self.plan)
        else:
            return 0

    def progress(self):

        if self.__paused_progress is not None:
            return self.__paused_progress

        d = self.duration()
        if d:
            p = (self.gameObject.time - self.start_time) / d
            return 1 if p > 1 else p
        else:
            return 1.0 if self.ready() else 0

    def ready(self):
        return self.duration() <= self.gameObject.time

    def do(self, action: Callable[[TimeLineProgressInfo], None], duration=0, absolute=None,
           continuous=False) -> Timeline:
        "Запланировать выполнение действия (action - функция)"
        if not self.plan:
            self.start_time = self.gameObject.time
            self.fired_time = -1

        self.plan.append(TimeEvent(absolute if absolute is not None else self.duration(), action, duration, continuous))

        return self

    def wait(self, duration) -> Timeline:
        "Запланировать задержку в сек"
        if not self.plan:
            self.start_time = self.gameObject.time
            self.fired_time = -1

        self.plan.append(TimeEvent(self.duration(), None, duration))

        return self

    def rewind(self, new_pos=0) -> Timeline:
        "Перемотать время на новую позицию, по умолч. на 0"

        def rew(*a, **b):
            self.start_time = self.gameObject.time + new_pos
            self.fired_time = new_pos - 0.01

        return self.do(rew)

    def repeat(self, times: int, from_pos=0):
        "Повторить times раз с позиции (по умолч. с 0)"

        def rew(*a, **b):
            nonlocal times
            if times > 0:
                self.start_time = self.gameObject.time + from_pos
                self.fired_time = from_pos - 0.01
            times -= 1

        return self.do(rew)

    def reset(self) -> Timeline:
        "Сбросить тайм лайн и все задания."

        def ne(*a, **b):
            self.plan = []
            self.start_time = self.gameObject.time
            self.fired_time = -1
            self.__paused_progress = None

        return self.do(ne)

    def pause(self) -> Timeline:

        if self.__paused_progress is None:
            self.__paused_progress = self.progress()

        return self

    def resume(self) -> Timeline:

        if self.__paused_progress is not None:
            d = self.fired_time - self.start_time
            self.start_time = self.gameObject.time - self.duration() * (1 - self.__paused_progress)
            self.fired_time = self.start_time + d
            self.__paused_progress = None

        return self

    def force_complete(self) -> Timeline:
        "Немедленно выполнить план"
        self.resume()
        self.start_time = self.gameObject.time - self.duration() - 0.001
        self.update(0)

        return self

    def kill(self):
        "Удалить тайм лайн из game object"

        def fi(*a, **bb):
            self.remove()

        self.do(fi)

        return self

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.__paused_progress is not None:
            return

        for gg in range(5):
            pt = self.gameObject.time - self.start_time
            pi = TimeLineProgressInfo()
            pi.entire_time = pt
            pi.entire_progress = self.progress()
            pi.timeline = self
            pi.deltaTime = deltaTime

            stt = self.start_time

            for i in self.plan:
                if (pt >= i.start_time > self.fired_time) or (i.continuous and (
                        i.start_time <= pt <= i.start_time + i.duration)):
                    if callable(i.action):
                        pi.section_time = pt - i.start_time
                        pi.section_progress = pi.section_time / i.duration if i.duration else 1
                        i.action(pi)
                        if stt != self.start_time:
                            break
            if stt == self.start_time:
                break

        self.fired_time = pt
