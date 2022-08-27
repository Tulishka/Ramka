import gc
from typing import Callable

from creature import Creature
from transport import Transport
from items_menu import ItemMenu
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
    prefabs = {}

    @staticmethod
    def init():

        GameManager.prefabs = {}
        GameManager.add_autogen_prefabs()
        GameManager.add_manual_prefabs()
        GameManager.add_saved_prefabs()

        GameManager.reset()

    @staticmethod
    def reset():
        lst = list(Game.get_objects())
        for l in lst:
            Game.remove_object(l)

        gc.collect()
        Game.add_object(DragAndDropController())
        Game.add_object(Camera(lock_y=True))
        Camera.main.uuid = "main_camera"
        Camera.main.get_uuid = lambda: Camera.main.uuid


    @staticmethod
    def prepare_scene(scene_name):

        def save_all(*a, **b):
            GameManager.save_scene()

        def trash(*a, **b):
            obj = DragAndDropController.controller.get_just_dragged_object(clas=BaseItem)
            if obj:
                Game.remove_object(obj)

        def save_prefab(*a, **b):
            obj = DragAndDropController.controller.get_just_dragged_object(clas=BaseItem)
            if obj:
                GameManager.save_as_prefab(obj)
                Game.remove_object(obj)

        def load(*a, **b):
            GameManager.reset()
            GameManager.prepare_scene(scene_name)

        def vis_if_drag():
            return DragAndDropController.controller.get_just_dragged_object(clas=BaseItem)

        def vis_not_drag():
            return not DragAndDropController.controller.get_just_dragged_object(clas=BaseItem)

        def vis_not_drag_shift():
            return pygame.key.get_mods() & pygame.KMOD_LSHIFT and not DragAndDropController.controller.get_just_dragged_object(clas=BaseItem)

        def items_menu(*a, **b):

            def create(prefab):
                o=GameManager.create_object_from_prefab(prefab,pos=Camera.main.mouse_world_pos()+Vector(0,prefab["object"].get_size().y/4),start_drag=True)
                Game.mouse_capture = o

            menu=ItemMenu(GameManager.get_prefabs(clas=GameObject),on_item_down=create)
            Game.add_object(menu,layer=Game.uiLayer)

        nav=NavBar("creature_select", row_direction=Vector(1, 0))
        nav.add_btn(IconableSprite("img/ui/plus.png").update_icon_args(size=40,border=(220,220,220), background=(150,150,150,200),border_radius=100),action=items_menu, action_on_mb_up=True, prefix="___")

        nav = NavBar("game_menu", pos=Vector(Game.ширинаЭкрана - 40, 40), row_direction=Vector(-1, 0))

        nav.add_btn(IconableSprite("img/ui/save.png"), action=save_all, action_on_mb_up=True, visible_func=vis_not_drag)
        nav.add_btn(IconableSprite("img/ui/load.png").update_icon_args(border=(255,0,0),background=(255,100,100)), action=load, action_on_mb_up=True, visible_func=vis_not_drag_shift)
        nav.add_btn(IconableSprite("img/ui/return.png"), action=save_prefab,  action_on_mb_up=True, visible_func=vis_if_drag)
        nav.add_btn(IconableSprite("img/ui/trash.png").update_icon_args(border=(255,0,0),background=(255,100,100)),  action_on_mb_up=True, action=trash, visible_func=vis_if_drag)


        rooms = [f"img/komnata{i if i > 1 else ''}.png" for i in [4, 2, 1, 3]]



        for i, kom in enumerate(rooms):
            room = Background(kom)
            ks = Game.высотаЭкрана / room.get_size().y, Game.высотаЭкрана / room.get_size().y
            room.transform.scale = ks
            rs=room.get_computed_size()
            rs[0]=round(rs[0])-1
            rs[1]=round(rs[1])
            room.transform.pos = rs.x * ((i - 1) + 0.5), Game.высотаЭкрана * 0.5
            Game.add_object(room)

        for i, kom in enumerate(rooms):
            wall = Background("img/wall.png")
            ks = Game.высотаЭкрана / room.get_size().y, Game.высотаЭкрана / room.get_size().y
            wall.transform.scale = ks
            wall.transform.pos = rs.x * i, Game.высотаЭкрана * 0.5
            Game.add_object(wall)

        cam_pos = CameraPos(min_x=-rs.x * 0.5, max_x=rs.x * (len(rooms) - 1.5))
        Game.add_object(cam_pos)
        Camera.main.set_focus(cam_pos, lock_y=True)

        # ======== load

        if not GameManager.load_scene(scene_name):
            GameManager.generate_manual()

        # ================ end load

        light = Lighting()
        Game.add_object(light, layer=Game.uiLayer)
        light.layer.change_order_first(light)

    @staticmethod
    def save_scene(filename="game.sav"):


        # print("game objects")
        # for z in Game.get_objects(clas=BaseItem):
        #     print(z.type_uid, z, z.origin)
        # print("====")
        # print("ui layer")
        # for z in Game.uiLayer.gameObjects:
        #     print(z)
        # print("====")
        # print("default layer")
        # for z in Game.defaultLayer.gameObjects:
        #     print(z)
        # print("====")

        output = []
        for o in Camera.main.get_children(clas=Savable):
            output.append(o.get_init_dict())
            # print(o.type_uid, o, o.origin)


        with open(filename, "w") as file:
            json.dump(output, file, indent=4)
            print("World saved!")

    @staticmethod
    def save_as_prefab(object: BaseItem):

        init = object.get_init_dict()

        pid = GameManager.add_prefab(lambda: GameManager.create_object_from_dict(init, add_to_game=False),
                                     origin="saved")

        with open(f".\\saved_prefabs\\{pid}.sav", "w") as file:
            json.dump(init, file, indent=4)
            print(f"prefab {pid} saved!")

    @staticmethod
    def create_object_from_dict(opts, parent=None, add_to_game=True) -> BaseItem:
        cls = GameManager.get_class(opts['class_name'])
        prm = cls.get_creation_params(opts, parent)
        obj = cls(*prm[0], **prm[1])

        if obj.transform.parent is None and parent:
            obj.transform.set_parent(parent, False)

        obj.init_from_dict(opts)

        if add_to_game:
            Game.add_object(obj)

        for ch in opts['children']:
            GameManager.create_object_from_dict(ch, parent=obj, add_to_game=add_to_game)

        if opts['children'] and add_to_game:
            obj.layer.sort_object_children(obj)

        return obj

    @staticmethod
    def load_scene(scene):
        filename = scene + ".sav"
        try:
            with open(filename, "r") as file:
                objects = json.load(file)
                for o in objects:
                    GameManager.create_object_from_dict(o)

                print("World loaded!")
                # for z in Game.get_objects(clas=BaseItem):
                #     print(z.type_uid,z,z.origin)
                return True
        except FileNotFoundError:
            return False

    @classmethod
    def generate_manual(cls):

        for f in GameManager.prefabs.values():
            p = GameManager.create_object_from_prefab(f, add_to_game=False)

            if p.transform.parent or p.transform.pos.length_squared() > 0:
                Game.add_object(p)

    @staticmethod
    def get_class(t):
        return eval(t)

    @staticmethod
    def add_prefab(prefab_factory: Callable[[], BaseItem], origin="manual"):

        def factory():
            obj = prefab_factory()
            obj.origin = origin
            return obj

        prefab_s = {
            "factory": prefab_factory,
            "origin": origin,
            "object": factory()
        }

        prefab = prefab_s["object"]
        GameManager.prefabs[prefab.type_uid] = prefab_s

        return prefab.type_uid

    @classmethod
    def add_manual_prefabs(cls):

        ap = GameManager.add_prefab

        ap(lambda: LightItem("mebel|window", (693, 278)))

        ap(lambda: Interier("mebel|bed2", (160, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90,
                                                                    accept_class=[Chelik, Pet]))

        ap(lambda: Interier("mebel|bed1", (1850, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90,
                                                                     accept_class=[Chelik, Pet]))

        ap(lambda: Interier("mebel|bed3", (2750, 540))
           .drop_zone_add("Sleep", Vector(-70, -85), radius=90, accept_class=[Chelik, Pet])
           .drop_zone_add("Sleep", Vector(70, -85), radius=90, accept_class=[Chelik, Pet]))

        ap(lambda: Pet("pets|oblachko", (700, 100)))

        ap(lambda: Pet("pets|kohka", (800, 100)))

        def t():
            p9 = Chelik("pers|p9", (500, 100))
            p9.drop_zone_add("LeftArm", Vector(-56, 107))
            p9.drop_zone_add("RightArm", Vector(60, 107))
            p9.drop_zone_add("Head", Vector(0, -130), radius=50)
            p9.image_offset = Vector(0, -30)
            return p9

        ap(t)

        ap(lambda: Chelik("pers|reb1", (500, 100))
           .drop_zone_add("LeftArm", Vector(-56, 107))
           .drop_zone_add("RightArm", Vector(60, 107))
           .drop_zone_add("Head", Vector(0, -130), radius=50)
           )

        ap(lambda: Chelik("pers|pusya", (600, 100)) \
           .drop_zone_add("LeftArm", Vector(-56, 107)) \
           .drop_zone_add("RightArm", Vector(60, 107)) \
           .drop_zone_add("Head", Vector(0, -130), radius=50)
           )

        ap(lambda: Bag("predmet|rykzak", (600, 100)).drop_zone_add("Bag", Vector(0, 0), max_items=100))
        ap(lambda: Transport("transport|Hors1", (600, 100)).drop_zone_add("Saddle", Vector(0, 0), radius=150))
        ap(lambda: HandableItem("predmet|telefon", (650, 100)))
        ap(lambda: Item("predmet|kormushka", (700, 100)))

    @classmethod
    def add_autogen_prefabs(cls):
        pass

    @classmethod
    def create_object_from_prefab(cls, prefab, add_to_game=True, pos=None, start_drag=False):
        p = prefab["factory"]()

        if add_to_game:
            Game.add_object(p)

        if pos:
            p.transform.pos = pos # p.transform.to_parent_local_coord(pos)

        if start_drag:
            DragAndDropController.controller.drag_now(p)

        return p

    @classmethod
    def add_saved_prefabs(cls):
        files = list(glob.glob(f".\\saved_prefabs\\*.sav"))

        def fac(op) -> Callable:
            return lambda: GameManager.create_object_from_dict(op, add_to_game=False)

        for f in files:
            with open(f, "r") as file:
                opts = json.load(file)
                GameManager.add_prefab(fac(opts), origin="saved")

    @classmethod
    def get_prefabs(cls, clas=None):
        for c in GameManager.prefabs.values():
            obj=c['object']
            if clas is None or isinstance(obj,clas):
                yield c


GameClasses.get_class = GameManager.get_class
