from typing import Tuple

from interier import Interier
from ramka.video_sprite import VideoSprite


class VideoInterier(Interier):
    def __init__(self, anim, pos, video_file: Tuple[str, Tuple[int, int]], video_pos, **kwargs):
        super().__init__(anim, pos, **kwargs)

        video_sprite = VideoSprite(video_file[0], size=video_file[1])
        video_sprite.pos(video_pos).transform.set_parent(self)

        self.video_file = video_file
        self.video_pos = video_pos

    @staticmethod
    def get_creation_params(dict, parent):
        p=super(VideoInterier,VideoInterier).get_creation_params(dict,parent)
        d=p[1]
        d.update({
            "video_file": dict["video_file"],
            "video_pos": dict["video_pos"],
        })
        return p[0], d

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "video_file": self.video_file,
            "video_pos": self.video_pos,
        })
        return res

