import random

from examples.Components.mini_map import MiniMapItem
from examples.ferma2.Fly_item import Fly_item
from ramka import Sprite, Cooldown, Vector, Game


class AvtomatIcon(MiniMapItem):

    def get_color(self):
        return (0, 240, 0)

    def get_radius(self):
        return 4

class Avtomat(AvtomatIcon,Sprite):
    def __init__(self, image, work_time=10, product_type=None, product_image=None, required_res={}, autostart=None,
                 product_count=1):
        super().__init__(image)
        self.res = {}
        self.required_res = required_res
        for k in self.required_res.keys():
            self.res[k] = 0
        self.busy_cd = Cooldown(work_time)
        self.product_type = product_type
        self.product_image = product_image
        self.onduty = False
        self.autostart = len(list(self.required_res.keys())) > 0 if autostart is None else autostart
        self.product_count = product_count

        self.deliver_zone_width = self.get_computed_size().x / 2
        self.deliver_zone_height = 50

    def can_accept_res(self, res_type):
        return res_type in self.required_res

    def add_res(self, res_type):
        if self.can_accept_res(res_type):
            self.res[res_type] += 1
            self.try_start()
            return True
        else:
            return False

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.autostart and not self.onduty:
            self.try_start()
        if self.job_finished():
            for i in range(self.product_count):
                self.deliver_product()

    def can_start(self):
        return self.busy_cd.ready and self.onduty == False and self.res_enough()

    def try_start(self):
        if self.can_start():
            if self.consume_res():
                self.busy_cd.start()
                self.onduty = True
                return True
        return False

    def job_finished(self):
        return self.busy_cd.ready and self.onduty

    def get_deliver_dest(self):
        tt = self.transform.pos + Vector(0, self.get_computed_size().y / 2)
        tt.x = tt.x + random.randint(-int(self.deliver_zone_width // 2), int(self.deliver_zone_width // 2))
        tt.y = tt.y + random.randint(0, self.deliver_zone_height)
        return tt

    def get_product_spawn(self):
        return self.transform.pos

    def create_product_item(self):
        it = Fly_item(self.product_image, self.get_deliver_dest(), pick_type=self.product_type)
        it.transform.pos = self.get_product_spawn()
        Game.add_object(it)
        return it

    def deliver_product(self):
        item = self.create_product_item()
        if item:
            self.onduty = False

    def res_enough(self):
        d = True
        for k in self.required_res.keys():
            d = self.required_res[k] <= self.res[k]
            if not d:
                break
        return d

    def consume_res(self):
        for k in self.required_res.keys():
            self.res[k] -= self.required_res[k]
        return True

    def get_resources_types(self):
        return self.res.keys()