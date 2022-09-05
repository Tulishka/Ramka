from typing import Callable, List, Union, Iterable, Any

from ramka import GameObject, Game


class ObjectGeneratorInterface:
    pass


class ObjectGenerator(ObjectGeneratorInterface, GameObject):
    def __init__(self,
                 factory: Callable[[ObjectGeneratorInterface], Any],
                 period: Union[float, Callable[[ObjectGeneratorInterface], float]],
                 count: Union[int, Callable[[ObjectGeneratorInterface, int], int], List[
                     Union[int, Callable[[ObjectGeneratorInterface, int], int]]]]
                 ):
        super().__init__()

        self.factory = factory
        self.period = period
        if not isinstance(count, Iterable):
            count = [count]
        self.count = count
        self.count_multiplier = 1.0

        self.__setup_interval(0)

    def __setup_interval(self, n):
        if n >= len(self.count):
            n = 0

        interval = (self.period(self) if callable(self.period) else self.period) / len(self.count)
        self.__index = n
        self.__remain_count = self.count[self.__index](self, self.__index) if callable(self.count[self.__index]) else \
            self.count[self.__index]
        self.__remain_count *= self.count_multiplier
        self.__dec_in_sec = self.__remain_count / interval
        self.__acc = 0
        self.__time_limit = interval

    def spawn(self, cnt):
        if self.factory:
            for i in range(cnt):
                a = self.factory(self)
                if isinstance(a, GameObject):
                    Game.add_object(a)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.__acc += deltaTime * self.__dec_in_sec
        self.__time_limit -= deltaTime

        if self.__acc >= 1:
            n = int(self.__acc)
            if n > self.__remain_count:
                n = self.__remain_count
            self.__acc -= n
            self.__remain_count -= n

            self.spawn(n)

        if self.__time_limit <= 0:
            self.__setup_interval(self.__index + 1)
