import random
from typing import List

import pygame.draw

from examples.ferma2.Fly_item import Fly_item
from examples.ferma2.Avtomat import Avtomat
from examples.ferma2.Kust import Kust
from examples.ferma2.Bot import Bot
from ramka import GameObject, Game, Vector


class Job:
    def __init__(self, job_type, pos, src_obj=None, dst_obj=None):
        self.pos = pos
        self.worker = None
        self.type = job_type
        self.src_obj = src_obj
        self.dst_obj = dst_obj
        self.time = Game.time
        self.canceled = False


class JobManager(GameObject):
    all_jobs = ['harvest_kust', 'harvest', 'plant', 'carrier']

    def __init__(self):
        super().__init__()
        self.jobs: List[Job] = []

    def update(self, deltaTime: float):
        super().update(deltaTime)

        #     актуализировать задачи
        cancel_jobs = [i for i in self.jobs if i.src_obj not in Game.gameObjects or (i.worker and i.worker not in Game.gameObjects)]
        for j in cancel_jobs:
            j.canceled = True
            j.worker = None
            self.jobs.remove(j)

        #     создать новые задачи

        t = "harvest_kust"
        vzad = [i.src_obj for i in self.jobs if i.type == t]
        kusts = Game.get_objects(clas=Kust, filter=lambda k: k not in vzad and k.state.animation == "rezult")
        for kust in kusts:
            self.jobs.append(Job(t, kust.transform.pos, kust))

        t = "harvest"
        vzad = [i.src_obj for i in self.jobs if i.type == t]
        avts = Game.get_objects(clas=Avtomat, filter=lambda k: k not in vzad and k.autostart is False and len(
            k.get_resources_types()) == 0)
        for avt in avts:
            it = len(
                list(Game.get_objects(clas=Fly_item, filter=lambda k: k.pick_type == avt.product_type))) < 3
            tr = it and len(list(Game.get_objects(clas=Avtomat,
                                                  filter=lambda k: k.can_accept_res(avt.product_type) and
                                                                   k.res[avt.product_type] < 3))) > 0
            if tr:
                self.jobs.append(Job(t, avt.transform.pos, avt))

        t = "plant"
        vzad = [i.src_obj for i in self.jobs if i.type == t]
        rosts = Game.get_objects(clas=Fly_item, filter=lambda k: k not in vzad and k.pick_type == 0)
        for rost in rosts:

            pp = Vector(random.randint(20, Game.ширинаЭкрана - 20),
                        random.randint(20, Game.высотаЭкрана - 20))
            test = Bot.kust_plant_test_spite
            test.transform.pos = pp
            test.prepare_image()
            for o in Game.get_objects():
                if test.is_collided(o):
                    pp = None
                    break

            if pp:
                self.jobs.append(Job(t, rost.transform.pos, rost, pp))

        t = "carrier"
        vzad = [i.src_obj for i in self.jobs if i.type == t]
        items = Game.get_objects(clas=Fly_item, filter=lambda i: i not in vzad and i.pick_type and not i.used)
        for item in items:
            objs = Game.get_objects(clas=Avtomat, filter=lambda a: a.can_accept_res(item.pick_type))
            for obj in objs:
                self.jobs.append(Job(t, item.transform.pos, item, obj))
                break

        Game.debug_str=str(len(self.jobs))

    def get_job(self, worker, job_types: List[str] = None):
        for j in self.jobs:
            if j.worker == worker:
                return j

        if job_types:
            for j in self.jobs:
                if j.worker is None and j.type in job_types:
                    j.worker=worker
                    return j

    def cancel_job(self, worker):
        j=self.get_job(worker)
        if j:
            j.canceled=True
            self.jobs.remove(j)

    def finish_job(self, worker):
        self.cancel_job(worker)

    def draw(self, dest: pygame.Surface):
        return
        for t in self.jobs:
            pygame.draw.circle(dest, (0, 0, 255), t.pos, 3)
            v=None
            if t.src_obj:
                v=t.src_obj.w_transform().pos
                pygame.draw.circle(dest, (255, 0, 0), v, 3)
            if isinstance(t.dst_obj,GameObject):
                v=t.dst_obj.w_transform().pos
                pygame.draw.circle(dest, (0, 255, 0), v, 3)
            if isinstance(t.dst_obj,Vector):
                v=t.dst_obj
                pygame.draw.circle(dest, (0, 255, 0), v, 3)
            if v:
                pygame.draw.line(dest,(100,100,100),t.pos,v)

