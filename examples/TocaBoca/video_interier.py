from typing import Tuple, Iterable, Union

from interier import Interier
from ramka import Game, Vector, interp_func_cubic
from ramka.gameobject_animators import ScaleAnimator
from ramka.video_sprite import VideoSprite


class VideoInterier(Interier):
    def __init__(self, anim, pos, video_file: Tuple[Union[str, Iterable[str]], Tuple[int, int]], video_pos, video_index=0, **kwargs):
        super().__init__(anim, pos, **kwargs)

        self.video_sprite = None

        self.video_file = [video_file[0]] if isinstance(video_file[0], str) else video_file[0], video_file[1]

        self.video_pos = video_pos
        self.video_index = video_index
        # self.create_video_object(False)

    def create_video_object(self, add_to_game):

        self.video_sprite = VideoSprite(self.video_file[0][self.video_index], size=self.video_file[1])
        self.video_sprite.pos(self.video_pos).transform.set_parent(self)

        if add_to_game:
            Game.add_object(self.video_sprite)

    def remove_video_object(self):
        if self.video_sprite:
            Game.remove_object(self.video_sprite)
            del self.video_sprite
            self.video_sprite = None

    @staticmethod
    def get_creation_params(dict, parent):
        p = super(VideoInterier, VideoInterier).get_creation_params(dict, parent)
        d = p[1]
        d.update({
            "video_file": dict["video_file"],
            "video_pos": dict["video_pos"],
            "video_index": dict.get("video_index",0),
        })
        return p[0], d

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "video_file": self.video_file,
            "video_pos": self.video_pos,
            "video_enabled": bool(self.video_sprite),
            "video_index":self.video_index,
        })
        return res

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        if opts.get("video_enabled", False):
            self.create_video_object(False)


    @Game.on_mouse_up
    def on_mouse_up(self, buttons):
        if self.mouse_start_point:
            if 1 in buttons:
                if self.video_sprite:
                    ScaleAnimator(self.video_sprite, Vector(1, 0.02), 0.15, interp_func=interp_func_cubic)().do(
                        lambda pi: self.remove_video_object()).kill()
                else:
                    self.create_video_object(True)
                    self.video_sprite.transform.scale = 1, 0.02
                    ScaleAnimator(self.video_sprite, Vector(1, 1), 0.15, interp_func=interp_func_cubic)().kill()
            elif 3 in buttons:
                self.video_index += 1
                if self.video_index >= len(self.video_file[0]):
                    self.video_index = 0

                self.remove_video_object()
                self.create_video_object(True)
