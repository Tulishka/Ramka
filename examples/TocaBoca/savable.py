import uuid
from typing import Dict

from ramka import Sprite, GameObject, Game, Camera


class Savable:

    def get_uuid(self):
        if not hasattr(self, "uuid"):
            self.uuid = str(uuid.uuid4())

        return self.uuid

    @staticmethod
    def get_creation_params(dict, parent) -> Dict:
        return [], {}

    def init_from_dict(self, dict: Dict[str, any]):

        if isinstance(self, GameObject):
            self.uuid = dict['uuid']
            self.transform.from_dict(dict['transform'])
            self.visible = dict.get('visible', True)
            self._parent_sort_me_by = dict['parent_sort_me_by']
            self.requested_layer_name = dict['layer']

            pr=self.get_parent()
            if (isinstance(pr, Camera) or pr is None) and abs(self.transform.pos.y)<5:
                self.transform.y = self.transform.y * Game.высотаЭкрана

            if isinstance(self, Sprite):
                self.image_rotate_offset = dict['image_rotate_offset']
                self.image_offset.x = dict['image_offset.x']
                self.image_offset.y = dict['image_offset.y']
                self.use_parent_mask = dict['use_parent_mask']

        return self

    def on_full_load(self):
        pass

    def get_init_dict(self):

        if isinstance(self, GameObject):
            pr = self.get_parent()
            p = self.get_parent().get_uuid() if pr and hasattr(pr, "get_uuid") else None
            if isinstance(pr, Camera) or pr is None:
                tr = self.transform.copy()
                tr.y = tr.y / Game.высотаЭкрана
            else:
                tr = self.transform

            res = {
                "uuid": self.get_uuid(),
                "parent": p,
                "class_name": type(self).__name__,
                "transform": tr.to_dict(),
                "parent_sort_me_by": self.parent_sort_me_by,
                "layer": self.layer.name if self.layer else self.requested_layer_name,
                "visible": self.visible,
            }

            if isinstance(self, Sprite):
                res.update({
                    "image_rotate_offset": self.image_rotate_offset,
                    "image_offset.x": self.image_offset.x,
                    "image_offset.y": self.image_offset.y,
                    "use_parent_mask": self.use_parent_mask,
                })

            childs = []
            for ch in self.get_children(clas=Savable):
                childs.append(ch.get_init_dict())
            res["children"] = childs
        else:
            res = {}

        return res
