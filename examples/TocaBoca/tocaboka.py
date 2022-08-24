from examples.Components.DragAndDrop import DragAndDropController
from background import Background
from bag import Bag
from camera_pos import CameraPos
from chelik import Chelik
from chelik_nav import NavBar
from creature import Creature
from handable_item import HandableItem
from interier import Interier
from item import Item
from lighting import Lighting, LightItem
from pet import Pet
from ramka import Game, Camera, Vector

Game.init('TocaBoca')
Game.цветФона = 250, 250, 250

# todo: перемещение камеры

rooms = [f"img/komnata{i if i > 1 else ''}.png" for i in [4, 2, 1, 3]]

Game.add_object(DragAndDropController())
cam_pos = CameraPos(min_x=-Game.ширинаЭкрана * 0.5, max_x=Game.ширинаЭкрана * (len(rooms) - 1.5))
Game.add_object(cam_pos)

nav = NavBar("creature_select")

for i, kom in enumerate(rooms):
    room = Background(kom)
    ks = Game.ширинаЭкрана / room.get_size().x, Game.ширинаЭкрана / room.get_size().x
    room.transform.scale = ks
    room.transform.pos = Game.ширинаЭкрана * ((i - 1) + 0.5), Game.высотаЭкрана * 0.5
    Game.add_object(room)

for i, kom in enumerate(rooms):
    wall = Background("img/wall.png")
    ks = Game.ширинаЭкрана / room.get_size().x, Game.ширинаЭкрана / room.get_size().x
    wall.transform.scale = ks
    wall.transform.pos = Game.ширинаЭкрана * (i), Game.высотаЭкрана * 0.5
    Game.add_object(wall)

Game.add_object(LightItem("mebel|window", (693, 278)))

Game.add_object(
    Interier("mebel|bed2", (160, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90, accept_class=[Chelik, Pet]))
Game.add_object(
    Interier("mebel|bed1", (1850, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90, accept_class=[Chelik, Pet]))
Game.add_object(
    Interier("mebel|bed3", (2750, 540)).drop_zone_add("Sleep", Vector(-70, -85), radius=90, accept_class=[Chelik, Pet])
        .drop_zone_add("Sleep", Vector(70, -85), radius=90, accept_class=[Chelik, Pet]))

Game.add_object(Pet("pets|oblachko", (700, 100)))
Game.add_object(Pet("pets|kohka", (800, 100)))

p9 = Chelik("pers|p9", (500, 100))
p9.drop_zone_add("LeftArm", Vector(-56, 107))
p9.drop_zone_add("RightArm", Vector(60, 107))
p9.drop_zone_add("Head", Vector(0, -130), radius=50)

p9.image_offset = Vector(0, -30)
Game.add_object(p9)

Game.add_object(Chelik("pers|reb1", (500, 100))
                .drop_zone_add("LeftArm", Vector(-56, 107))
                .drop_zone_add("RightArm", Vector(60, 107))
                .drop_zone_add("Head", Vector(0, -130), radius=50)
                )
pusya = Chelik("pers|pusya", (600, 100)) \
    .drop_zone_add("LeftArm", Vector(-56, 107)) \
    .drop_zone_add("RightArm", Vector(60, 107)) \
    .drop_zone_add("Head", Vector(0, -130), radius=50)

Game.add_object(pusya)

Game.add_object(Bag("predmet|rykzak", (600, 100)).drop_zone_add("Bag", Vector(0, 0), max_items=100))
Game.add_object(HandableItem("predmet|telefon", (650, 100)))
Game.add_object(Item("predmet|kormushka", (700, 100)))

camera = Camera(lock_y=True, target=cam_pos)
Game.add_object(camera)

Game.add_object(Lighting(), layer=Game.uiLayer)



# for i in Game.get_objects(clas=Creature):
#     nav.add_btn(i, "0" if isinstance(i, Chelik) else "1")

Game.run()
