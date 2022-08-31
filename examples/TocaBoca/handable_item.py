from item import Item
from ramka.gameobject_animators import AngleAnimator


class HandableItem(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.update_icon_args(angle=-45)

    def on_attach(self, dz):
        super().on_attach(dz)
        angle=0
        if dz.trigger_name == "LeftArm":
            angle = 45
        elif dz.trigger_name == "RightArm":
            angle = -45
        elif dz.trigger_name in ("Head", "Sleep", "Flat"):
            sz = self.get_size()
            if sz[1] > sz[0]:
                angle = -90

        if angle:
            # self.transform.angle=angle
            AngleAnimator(self,angle,0.2)().kill()

        dz.update_attached_object_pos(self)

    def on_detach(self, dz):
        super().on_detach(dz)
        if self.transform.angle:
            # self.transform.angle = 0
            AngleAnimator(self, 0, 0.2)().kill()
