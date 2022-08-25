from examples.Components.DragAndDrop import DragAndDropController
from game_classes import GameClasses
from iconable import IconableSprite
from ramka import Game, Camera, Vector

import json
from background import Background
from nav_bar import NavBar
from camera_pos import CameraPos

# savables ===========================
from bag import Bag
from chelik import Chelik
from handable_item import HandableItem
from interier import Interier
from item import Item
from pet import Pet
from lighting import Lighting, LightItem
from base_item import *


# savables ===========================

class GameManager:

    @staticmethod
    def init():
        GameManager.reset()

    @staticmethod
    def reset():
        lst = list(Game.get_objects())
        for l in lst:
            Game.remove_object(l)

        Game.add_object(DragAndDropController())
        Game.add_object(Camera(lock_y=True))
        Camera.main.uuid = "main_camera"

    @staticmethod
    def prepare_scene(scene_name):

        def save(*a, **b):
            GameManager.save()

        def load(*a, **b):
            GameManager.reset()
            GameManager.prepare_scene(scene_name)

        NavBar("creature_select",row_direction=Vector(1,0))

        nav = NavBar("game_menu",pos=Vector(Game.ширинаЭкрана-40,40), row_direction=Vector(0, 1))

        nav.add_btn(IconableSprite("img/ui/save.png"),  action=save, action_on_mb_up=True)
        nav.add_btn(IconableSprite("img/ui/load.png"),  action=load, action_on_mb_up=True)

        rooms = [f"img/komnata{i if i > 1 else ''}.png" for i in [4, 2, 1, 3]]

        cam_pos = CameraPos(min_x=-Game.ширинаЭкрана * 0.5, max_x=Game.ширинаЭкрана * (len(rooms) - 1.5))
        Game.add_object(cam_pos)
        Camera.main.set_focus(cam_pos, lock_y=True)

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

        # ======== load

        GameManager.load_scene(scene_name)

        # ================ end load

        light = Lighting()
        Game.add_object(light, layer=Game.uiLayer)
        light.layer.change_order_first(light)

    @staticmethod
    def save(filename="game.sav"):
        output = []
        for o in Camera.main.get_children(clas=Savable):
            output.append(o.get_init_dict())

        with open(filename, "w") as file:
            json.dump(output, file, indent=4)
            print("World saved!")

    @staticmethod
    def create_object_from_dict(opts, parent=None):
        cls = GameManager.get_class(opts['class_name'])
        prm = cls.get_creation_params(opts)
        obj = cls(*prm[0], **prm[1])
        obj.init_from_dict(opts)

        if obj.transform.parent is None and parent:
            obj.transform.set_parent(parent, False)

        Game.add_object(obj, Game.get_layer(opts['layer']))

        for ch in opts['children']:
            ch['parent'] = obj
            GameManager.create_object_from_dict(ch, obj)

        if opts['children']:
            obj.layer.sort_object_children(obj)

        return obj

    @staticmethod
    def load(filename="game.sav"):
        try:
            with open(filename, "r") as file:
                objects = json.load(file)
                for o in objects:
                    GameManager.create_object_from_dict(o)

                print("World loaded!")
                return True
        except FileNotFoundError:
            return False

    @classmethod
    def load_scene(cls, scene_name):

        if GameManager.load():
            return

        Game.add_object(LightItem("mebel|window", (693, 278)))

        Game.add_object(
            Interier("mebel|bed2", (160, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90,
                                                             accept_class=[Chelik, Pet]))
        Game.add_object(
            Interier("mebel|bed1", (1850, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90,
                                                              accept_class=[Chelik, Pet]))
        Game.add_object(
            Interier("mebel|bed3", (2750, 540)).drop_zone_add("Sleep", Vector(-70, -85), radius=90,
                                                              accept_class=[Chelik, Pet])
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

    @staticmethod
    def get_class(t):
        return eval(t)


GameClasses.get_class = GameManager.get_class
