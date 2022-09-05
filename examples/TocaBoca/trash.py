from movable import Movable
from base_item import DropZone
from interier import Interier
from ramka import Sprite, Game, Vector
from ramka.effects import Effects
from ramka.gameobject_animators import ScaleAnimator, PosAnimator


class Trash(Interier):
    def __init__(self, *a, **b):
        super(Trash, self).__init__(*a, **b)
        self.eff = Effects(self)

    def on_object_attached(self, dz: DropZone, obj: Movable):
        obj.allow_dragging=False
        ScaleAnimator(obj, Vector(0.01), 0.2, delay=0.2)().do(lambda x: Game.remove_object(obj)).kill()

        def aaa(tt):
            PosAnimator(obj, Vector(0.0, 60), 0.15)().kill()

        self.eff.pulse(1.1, 0.6)
        self.timers.set_timeout(0.2,aaa)

