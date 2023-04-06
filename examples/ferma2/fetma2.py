import random

from examples.Components.DragAndDrop import DragAndDropController
from examples.Components.mini_map import MiniMap
from examples.ferma2.Bot import Carrier_bot, Sadavad_bot, Hayrester_bot
from examples.ferma2.Igrok import Igrok
from examples.ferma2.JobManager import JobManager
from examples.ferma2.Magazins import Magazin1, Magazin2, Kafe
from examples.ferma2.Melinica import Melinica
from examples.ferma2.Pech import Pech
from examples.ferma2.Pet import Pet
from examples.ferma2.Ugol import Ugol
from ramka import Game, Camera

Game.init('ферма')
Game.цветФона = 186, 184, 108

man = JobManager()
Game.add_object(man)

kafe = Kafe()
Game.add_object(kafe)
kafe.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана - 200

pech = Pech()
Game.add_object(pech)
pech.transform.pos = 74, 74

ugol = Ugol()
Game.add_object(ugol)
ugol.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана / 5

mel = Melinica()
Game.add_object(mel)
mel.transform.pos = Game.ширинаЭкрана - mel.get_size().x / 2, mel.get_size().y / 2

m = Magazin1()
Game.add_object(m)
m.transform.pos = 90, Game.высотаЭкрана - 200

m2 = Magazin2()
Game.add_object(m2)
m2.transform.pos = Game.ширинаЭкрана - 100, Game.высотаЭкрана - 200

boti = [Carrier_bot, Carrier_bot, Carrier_bot, Sadavad_bot, Sadavad_bot, Hayrester_bot]
for k in boti:
    cr = k()
    Game.add_object(cr)
    cr.transform.pos = Game.ширинаЭкрана / 2 + random.randint(-20, 20), Game.высотаЭкрана / 2 + random.randint(-20, 20)

igr = Igrok()
Game.add_object(igr)
igr.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2

pet = Pet(igr)
Game.add_object(pet)
pet.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2

Game.add_object(DragAndDropController())

Game.defaultLayer.change_order_last(man)

Game.add_object(MiniMap(), layer=Game.uiLayer)

camera = Camera(igr,lock_y=True)
Game.add_object(camera)

Game.run()
