class Timers:
    def __init__(self):
        self.__timers = {}
        self.__timer_id = 0

    def set_interval(self, time: float, callback: callable, timer_id=None) -> any:
        if not timer_id:
            self.__timer_id += 1
            timer_id = self.__timer_id

        self.__timers[timer_id] = {
            "interval": time,
            "value": time,
            "callback": callback
        }
        return timer_id

    def set_timeout(self, time: float, callback: callable, timer_id=None) -> any:
        if not timer_id:
            self.__timer_id += 1
            timer_id = self.__timer_id

        self.__timers[timer_id] = {
            "interval": 0,
            "value": time,
            "callback": callback
        }
        return timer_id

    def clear_all(self):
        self.__timers = {}

    def clear_timer(self, timer_id):
        if timer_id in self.__timers:
            del self.__timers[timer_id]

    def update(self, deltaTime: float):
        for tid in list(self.__timers.keys()):
            t = self.__timers[tid]
            t["value"] -= deltaTime
            if t["value"] < 0:
                t["callback"](tid)
                if tid in self.__timers:
                    t["value"] = t["interval"]
                    if t["value"] == 0:
                        del self.__timers[tid]
