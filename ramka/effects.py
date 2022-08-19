from ramka import Component, interp_pulse
from ramka.timeline import Timeline, TimeLineProgressInfo


class Effects(Component):
    def __init__(self, game_object):
        super().__init__(game_object)

    def pulse(self, koef=1.2):
        t = self.gameObject.get_components(Timeline, self.pulse.__name__)
        for i in t: return
        interp = interp_pulse((1, koef), (0, 1))

        initial_scale = abs(self.gameObject.transform.scale.elementwise())

        def scaling(pi: TimeLineProgressInfo):
            sc = interp(pi.section_progress)
            self.gameObject.transform.scale_xy = initial_scale.x * sc, initial_scale.y * sc

        def reset(pi: TimeLineProgressInfo):
            self.gameObject.transform.scale_xy = initial_scale

        tl = Timeline(self.gameObject, self.pulse.__name__)
        tl.do(scaling, duration=0.5, continuous=True).do(reset).kill()

    def hop(self, height=60):
        t = self.gameObject.get_components(Timeline, self.hop.__name__)
        for i in t: return

        interp = interp_pulse((1, 1), (0, 0))
        initial = self.gameObject.transform.y

        def eff(pi: TimeLineProgressInfo):
            sc = interp(pi.section_progress)
            self.gameObject.transform.y = initial - sc * height

        def reset(pi: TimeLineProgressInfo):
            self.gameObject.transform.y = initial

        tl = Timeline(self.gameObject, self.hop.__name__)
        tl.do(eff, duration=0.5, continuous=True).do(reset).kill()

    def flip(self, direction=1):
        t = self.gameObject.get_components(Timeline, self.flip.__name__)
        for i in t: return

        interp = interp_pulse((1, 1), (0, 0), 2)
        initial = self.gameObject.transform.angle

        def eff(pi: TimeLineProgressInfo):
            sc = interp(pi.section_progress)
            self.gameObject.transform.angle = initial + direction * sc * 360

        def reset(pi: TimeLineProgressInfo):
            self.gameObject.transform.angle = initial

        tl = Timeline(self.gameObject, self.flip.__name__)
        tl.do(eff, duration=0.5, continuous=True).do(reset).kill()
