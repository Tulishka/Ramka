from random import choice
from typing import List, Union

from base_item import TriggerZone, BaseItem

from ramka import Vector, Game, Camera


class DispenserZone(TriggerZone):

    def __init__(self, parent: BaseItem, name, prefab_names: Union[List[str], str], **kwargs):
        super().__init__(parent, name, **kwargs)

        if isinstance(prefab_names, str):
            prefab_names = [prefab_names]

        self.prefab_names = prefab_names

    @staticmethod
    def get_creation_params(dict, parent):
        m = super(DispenserZone,DispenserZone).get_creation_params(dict, parent)
        z = m[1]
        z.update({
            "prefab_names": dict["prefab_names"],
        })
        return m[0], z

    def init_from_dict(self, opts):
        super().init_from_dict(opts)

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "prefab_names": self.prefab_names,
        })
        return res

    @Game.on_mouse_down(button=1)
    def on_mouse_down(self):
        if not self.interactive():
            from game_manager import GameManager
            prefab = choice(self.prefab_names)
            GameManager.create_object_from_prefab(prefab,pos=Camera.main.mouse_world_pos(),start_drag=True)
