from ramka import Game


class Cooldown:

    def __init__(self, interval=99999):
        """ interval - время "остывания" в сек """
        self.__start_time = Game.time-99999
        self.interval = interval

    def reset(self):
        """ Сброс процесса остывания """
        self.__start_time = Game.time - self.interval

    def __call__(self, *args, **kwargs):
        return self.ready

    @property
    def ready(self):
        """ Остывание завершено? """
        return self.__start_time + self.interval < Game.time

    @property
    def progress(self):
        """ Прогресс остывание - число от 0 до 1 """
        if self.interval == 0:
            return 1
        a = (Game.time - self.__start_time) / self.interval
        return 1 if a > 1 else a

    def start(self):
        """Вызвать когда нужно начать отсчет времени "остывания" """
        self.__start_time = Game.time
