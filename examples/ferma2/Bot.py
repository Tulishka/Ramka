import random
import pygame

from examples.Components.DragAndDrop import Draggable
from examples.Components.mini_map import MiniMapItem
from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Fly_item import Fly_item

from examples.ferma2.Kust import Kust
from examples.ferma2.Magazins import Kafe
from ramka import Sprite, Game, Vector


class BotIcon(MiniMapItem):

    def get_color(self):
        return (255, 0, 0)

    def get_radius(self):
        return 2


class Bot(BotIcon, Draggable, Sprite):
    all_jobs = ['harvest_kust', 'harvest', 'plant', 'carrier']
    F_C_SPD = 1
    F_G_SPD = 20
    F_WC_SPD = 0.01
    MAX_FOOD = 100
    kust_plant_test_spite = None

    def __init__(self, ani="ira_sprites/steavkres.png"):
        super().__init__(ani)

        from examples.ferma2.JobManager import JobManager

        self.carry = None

        self.spd = 250
        self.job = ""
        self.jobs = Bot.all_jobs
        self.food = Bot.MAX_FOOD

        self.jman: JobManager = list(Game.get_objects(clas=JobManager))[0]

        if not Bot.kust_plant_test_spite:
            Bot.kust_plant_test_spite = Sprite("ira_sprites/kust.png")

    # def old_update(self, deltaTime: float):
    #     super().update(deltaTime)
    #
    #     old_pos = self.transform.pos
    #
    #     if self.item and (self.item not in Game.gameObjects):
    #         self.item = None
    #         self.carry = False
    #         self.path = None
    #         self.job = ""
    #
    #     if self.food < 0 and not self.item:
    #         self.job = "hangry"
    #
    #     if self.job == "hangry":
    #         kafe = list(Game.get_objects(clas=Kafe))
    #         kafe = kafe[0]
    #         if self.is_collided(kafe):
    #             self.food += Bot.F_G_SPD * deltaTime
    #         else:
    #             self.transform.move_toward_ip(kafe, self.spd * deltaTime)
    #         if self.food > Bot.MAX_FOOD:
    #             self.job = ""
    #
    #     if self.job == "":
    #         self.job = random.choice(self.jobs)
    #
    #     if self.job == "carrier":
    #         if self.item is None:
    #             obj = list(Game.get_objects(clas=Fly_item, filter=lambda i: i.pick_type and not i.used))
    #             if len(obj) > 0:
    #                 obj = random.choice(obj)
    #                 self.item = obj
    #                 obj.used = True
    #             else:
    #                 self.job = ""
    #
    #         if self.item:
    #             if not self.carry:
    #                 info = {}
    #                 self.transform.move_toward_ip(self.item, self.spd * deltaTime, step_info=info)
    #                 if info["delta"].length_squared() == 0:
    #                     self.carry = True
    #                     self.item.target = None
    #                     self.item.transform.set_parent(self, from_world=True)
    #             else:
    #                 if self.path is None:
    #                     obj = list(
    #                         Game.get_objects(clas=Avtomat, filter=lambda a: a.can_accept_res(self.item.pick_type)))
    #                     if len(obj) > 0:
    #                         self.path = obj[0]
    #                 else:
    #                     self.transform.move_toward_ip(self.path, self.spd * deltaTime)
    #                     if self.is_collided(self.path):
    #                         self.path.add_res(self.item.pick_type)
    #                         Game.remove_object(self.item)
    #                         self.job = ""
    #
    #     if self.job == "harvest_kust":
    #         kust = list(Game.get_objects(clas=Kust, filter=lambda k: k.state.animation == "rezult"))
    #         if len(kust) > 0:
    #             kust = kust[0]
    #             self.transform.move_toward_ip(kust, self.spd * deltaTime)
    #             if self.is_collided(kust):
    #                 kust.harvest()
    #                 self.job = ""
    #         else:
    #             self.job = ""
    #
    #     if self.job == "harvest":
    #         avts = list(Game.get_objects(clas=Avtomat, filter=lambda k: k.autostart is False and len(
    #             k.get_resources_types()) == 0))
    #         if len(avts) > 0:
    #             cont = False
    #             for avt in avts:
    #                 it = len(
    #                     list(Game.get_objects(clas=Fly_item, filter=lambda k: k.pick_type == avt.product_type))) < 3
    #                 tr = it and len(list(Game.get_objects(clas=Avtomat,
    #                                                       filter=lambda k: k.can_accept_res(avt.product_type) and
    #                                                                        k.res[avt.product_type] < 3))) > 0
    #                 if tr:
    #                     cont = True
    #                     self.transform.move_toward_ip(avt, self.spd * deltaTime)
    #                     if self.is_collided(avt):
    #                         avt.try_start()
    #                         cont = False
    #                     break
    #             if not cont:
    #                 self.job = ""
    #
    #         else:
    #             self.job = ""
    #
    #     if self.job == "plant":
    #         if self.item is None:
    #             rosts = list(Game.get_objects(clas=Fly_item, filter=lambda k: k.pick_type == 0 and not k.used))
    #             if len(rosts) > 0:
    #                 self.item = random.choice(rosts)
    #                 self.item.used = True
    #
    #         if self.item:
    #             if not self.carry:
    #                 info = {}
    #                 self.transform.move_toward_ip(self.item, self.spd * deltaTime, step_info=info)
    #                 if info["delta"].length_squared() == 0:
    #                     self.carry = True
    #                     self.item.target = None
    #                     self.path = None
    #                     self.item.transform.set_parent(self, from_world=True)
    #             else:
    #                 if self.path is None:
    #                     self.path = Vector(random.randint(20, Game.ширинаЭкрана - 20),
    #                                        random.randint(20, Game.высотаЭкрана - 20))
    #                     test = Bot.kust_plant_test_spite
    #                     test.transform.pos = self.path
    #                     test.prepare_image()
    #                     for o in Game.get_objects():
    #                         if test.is_collided(o):
    #                             self.path = None
    #                             break
    #                 else:
    #                     info = {}
    #                     self.transform.move_toward_ip(self.path, self.spd * deltaTime, step_info=info)
    #                     if info["delta"].length_squared() == 0:
    #                         self.job = ""
    #                         self.carry = False
    #                         self.path = None
    #                         Game.remove_object(self.item)
    #                         self.item = None
    #                         kust = Kust()
    #                         Game.add_object(kust)
    #                         kust.transform.pos = self.transform.pos
    #         else:
    #             self.job = ""
    #
    #     delta_pos = (self.transform.pos - old_pos).length()
    #     self.food -= Bot.F_C_SPD * deltaTime + delta_pos * Bot.F_WC_SPD

    def update(self, deltaTime: float):
        super().update(deltaTime)

        old_pos = self.transform.pos

        if self.carry:
            if self.carry not in Game.gameObjects:
                self.carry = None

        if self.food < 0:
            self.job = "hangry"

        if self.job == "hangry":
            kafe = list(Game.get_objects(clas=Kafe))
            kafe = kafe[0]
            if self.is_collided(kafe):
                self.food += Bot.F_G_SPD * deltaTime
            else:
                self.transform.move_toward_ip(kafe, self.spd * deltaTime)
            if self.food > Bot.MAX_FOOD:
                self.job = ""
        else:

            job = self.jman.get_job(self,self.jobs)

            if job:
                self.job = job.type

                if self.job == "carrier":
                    if not self.carry:
                        info = {}
                        self.transform.move_toward_ip(job.src_obj, self.spd * deltaTime, step_info=info)
                        if info["delta"].length_squared() == 0:
                            self.carry = job.src_obj
                            job.src_obj.target = None
                            job.src_obj.transform.set_parent(self, from_world=True)
                    else:
                        self.transform.move_toward_ip(job.dst_obj, self.spd * deltaTime)
                        if self.is_collided(job.dst_obj):
                            self.carry=None
                            job.dst_obj.add_res(job.src_obj.pick_type)
                            Game.remove_object(job.src_obj)
                            self.jman.finish_job(self)

                if self.job == "harvest_kust":
                    self.transform.move_toward_ip(job.src_obj, self.spd * deltaTime)
                    if self.is_collided(job.src_obj):
                        job.src_obj.harvest()
                        self.jman.finish_job(self)

                if self.job == "harvest":
                    self.transform.move_toward_ip(job.src_obj, self.spd * deltaTime)
                    if self.is_collided(job.src_obj):
                        job.src_obj.try_start()
                        self.jman.finish_job(self)

                if self.job == "plant":
                    if not self.carry:
                        info = {}
                        self.transform.move_toward_ip(job.src_obj, self.spd * deltaTime, step_info=info)
                        if info["delta"].length_squared() == 0:
                            self.carry = job.src_obj
                            job.src_obj.target = None
                            job.src_obj.transform.set_parent(self, from_world=True)
                    else:
                        info = {}
                        self.transform.move_toward_ip(job.dst_obj, self.spd * deltaTime, step_info=info)
                        if info["delta"].length_squared() == 0:
                            self.carry = None
                            Game.remove_object(job.src_obj)
                            kust = Kust()
                            Game.add_object(kust)
                            kust.transform.pos = self.transform.pos
                            self.jman.finish_job(self)
            else:
                self.job=""

        delta_pos = (self.transform.pos - old_pos).length()
        self.food -= Bot.F_C_SPD * deltaTime + delta_pos * Bot.F_WC_SPD

    def draw(self, dest: pygame.Surface):
        super().draw(dest)
        # a = Game.font.render(str(self.job)+", "+str(round(self.food,2)), True, (255, 255, 255))
        # dest.blit(a, (self.transform.x, self.transform.y))


class Sadavad_bot(Bot):
    def __init__(self):
        super().__init__("ira_sprites/steavkressad.png")
        self.jobs = ["plant", "harvest_kust"]


class Carrier_bot(Bot):
    def __init__(self):
        super().__init__("ira_sprites/steavkrescar.png")
        self.jobs = ["carrier"]


class Hayrester_bot(Bot):
    def __init__(self):
        super().__init__("ira_sprites/steavkreshar.png")
        self.jobs = ["harvest"]
