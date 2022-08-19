from ramka import Component, GameObject, Vector


class PathMovingComponent(Component):
    def __init__(self, obj: GameObject):
        super().__init__(game_oject=obj)
        self.currP = -1
        self.napr = 1
        self.path = None
        self.pinpong = 0
        self.spd = 350
        self.trg = None
        self.wait = 0
        self.wait_to = 0

    def next_point(self):
        if self.path:
            self.currP = self.currP + self.napr
            if self.currP >= len(self.path) or self.currP < 0:
                if self.pinpong:
                    self.napr = self.napr * -1
                    self.currP = self.currP + self.napr * 2
                else:
                    self.currP = -1
                    self.path = None

            if self.currP >= 0:
                self.trg = Vector(self.path[self.currP])

            self.wait_to = self.gameObject.time + self.wait

    def update(self, deltaTime: float):
        super().update(deltaTime)

        tr = self.gameObject.transform

        if self.wait_to > self.gameObject.time or not self.trg:
            return

        nnt = self.trg - tr.pos
        dst = nnt.length()
        if dst > 0:
            nnt.normalize_ip()
            cc = self.spd * deltaTime
            if dst < cc:
                cc = dst
            tr.pos = tr.pos + cc * nnt
        else:
            self.next_point()

        if nnt.x < 0:
            tr.scale_x = abs(tr.scale_x)
        if nnt.x > 0:
            tr.scale_x = abs(tr.scale_x) * -1

    def set_path(self, path, pingpong=0):
        self.path = path
        self.currP = -1
        self.napr = 1
        self.pinpong = pingpong
        self.next_point()