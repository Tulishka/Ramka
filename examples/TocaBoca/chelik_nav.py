from ramka import Sprite, Game, Camera, Transform
from ramka.effects import Effects
from ramka.gameobject_animators import PosAnimator


class NavBtn(Sprite):
    def __init__(self,anim, chelik):
        super().__init__(anim)
        self.chelik = chelik
        self.eff=Effects(self)

    @Game.on_mouse_down(button=1)
    def on_mouse_down(self):
        self.eff.pulse(duration=0.2)
        PosAnimator(Camera.main.target,self.chelik.transform.pos,0.5)().kill()
        # Camera.main.target.transform.pos= self.chelik.transform.pos