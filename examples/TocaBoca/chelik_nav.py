from ramka import Sprite, Game, Camera, Transform, interp_pulse, Vector, interp_mid_spd
from ramka.effects import Effects
from ramka.gameobject_animators import PosAnimator


class NavBtn(Sprite):
    def __init__(self, anim, chelik):
        super().__init__(anim)
        self.chelik = chelik
        self.eff = Effects(self)

    @Game.on_mouse_down(button=1)
    def on_mouse_down(self):
        self.eff.pulse(duration=0.2)

        def tap(t):
            self.chelik.eff.pulse(duration=0.5,koef=1.05)

        pos = Transform.to_local_coord(Camera.main.transform, self.chelik.transform)

        f = interp_mid_spd((1, pos - Camera.main.target.transform.pos), (0, Vector(0)))

        PosAnimator(Camera.main.target, pos, 0.5, interp_func=f)().do(tap,0.5).kill()
