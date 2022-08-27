import pygame

from ramka import Sprite


class Iconable:

    def set_icon_args(self, **args):
        self._icon_args = args
        return self

    def update_icon_args(self, **args):
        self._get_icon_args().update(args)
        return self

    def def_icon_args(self):
        self.set_icon_args(size=55, offset=(0, 0), background=(100, 150, 100), border=(50, 110, 50), border_radius=16)
        return self

    def _get_icon_args(self):
        if not hasattr(self, "_icon_args"):
            self.def_icon_args()
        return getattr(self, "_icon_args", {})

    def get_icon(self):
        return self._get_icon(**self._get_icon_args())

    @staticmethod
    def create_icon_image(image: pygame.Surface, size=55, offset=(0, 0), background=(100, 150, 100),
                          border=(50, 110, 50),
                          border_radius=16):

        sz = image.get_size()
        pw = size - size // 7
        k = pw / sz[0]
        x = (size - pw) / 2
        y = (size - int(k * sz[1])) / 2
        res = pygame.Surface((size, size), flags=pygame.SRCALPHA)
        res.fill(background)
        res.blit(
            pygame.transform.smoothscale(image, (pw, int(k * sz[1]))),
            (x + offset[0] * k * sz[0], y + offset[1] * k * sz[1])
        )

        ms = pygame.Surface((size, size), flags=pygame.SRCALPHA)
        pygame.draw.rect(ms, (255, 255, 255), pygame.Rect(0, 0, size, size), border_radius=border_radius)
        mask = pygame.mask.from_surface(ms)
        mask.to_surface(res, res, unsetcolor=(0, 0, 0, 0))
        pygame.draw.rect(res, border, pygame.Rect(0, 0, size, size), 3, border_radius=border_radius)

        return res

    def _get_icon(self, size=55, offset=(0, 0), background=(100, 150, 100), border=(50, 110, 50),
                  animation_name: str = None, border_radius=16):

        if isinstance(self, Sprite):
            if animation_name is None:
                animation_name = self.state.animation

            if not animation_name:
                ani = self.curr_animation()
            else:
                ani = self.animations.get(animation_name)
                if not ani:
                    ani = self.curr_animation()

            return Iconable.create_icon_image(ani.get_image(0), size, offset, background, border, border_radius)

        else:
            raise Exception("use Iconable as mixin for Sprite class only")


class IconableSprite(Iconable, Sprite):
    def def_icon_args(self):
        self._icon_args = {
            "border": (200, 200, 255),
            "background": (180, 180, 220)
        }
        return self
