from examples.Components.DragAndDrop import Draggable, DragAndDropController
from examples.TocaBoca.background import Background
from examples.TocaBoca.bag import Bag
# from examples.TocaBoca.camera_pos import CameraPos
from examples.TocaBoca.chelik import Chelik
from examples.TocaBoca.handable_item import HandableItem
from examples.TocaBoca.interier import Interier
from examples.TocaBoca.item import Item
from examples.TocaBoca.pet import Pet
from ramka import Game, Camera, Vector

Game.init('TocaBoca')
Game.цветФона = 250, 250, 250

# todo: перемещение камеры


Game.add_object(DragAndDropController())

komnata2 = Background("img/komnata2.png")
ks = Game.ширинаЭкрана / komnata2.get_size().x, Game.ширинаЭкрана / komnata2.get_size().x
komnata2.transform.scale = ks
komnata2.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2
Game.add_object(komnata2)
komnata1 = Background("img/komnata.png")
komnata1.transform.scale = ks
komnata1.transform.pos = Game.ширинаЭкрана / 2 + Game.ширинаЭкрана, Game.высотаЭкрана / 2
Game.add_object(komnata1)

Game.add_object(
    Interier("mebel|bed2", (150, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90, accept_class=[Chelik, Pet]))
Game.add_object(Interier("mebel|window", (693, 278)))

Game.add_object(Pet("pets|oblachko", (700, 100)))
Game.add_object(Pet("pets|kohka", (800, 100)))

Game.add_object(Chelik("pers|p9", (500, 100))
                .drop_zone_add("LeftArm", Vector(-56, 107))
                .drop_zone_add("RightArm", Vector(60, 107))
                .drop_zone_add("Head", Vector(0, -130), radius=50)
                )


Game.add_object(Chelik("pers|reb1", (500, 100))
                .drop_zone_add("LeftArm", Vector(-56, 107))
                .drop_zone_add("RightArm", Vector(60, 107))
                .drop_zone_add("Head", Vector(0, -130), radius=50)
                )


Game.add_object(Chelik("pers|pusya", (600, 100))
                .drop_zone_add("LeftArm", Vector(-56, 107))
                .drop_zone_add("RightArm", Vector(60, 107))
                .drop_zone_add("Head", Vector(0, -130), radius=50)
                )


Game.add_object(Bag("predmet|rykzak", (600, 100)).drop_zone_add("Bag", Vector(0, 0), max_items=100))
Game.add_object(HandableItem("predmet|telefon", (650, 100)))
Game.add_object(Item("predmet|kormushka", (700, 100)))

# cam_pos = CameraPos()
# Game.add_object(cam_pos)

camera = Camera(lock_y=True)
Game.add_object(camera)



Game.run()
