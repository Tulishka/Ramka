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
                          border_radius=16, angle=0, scale_contain=False):

        if angle:
            image = pygame.transform.rotate(image, angle)
        sz = image.get_size()
        pw = size - size // 7
        if pw > sz[0]:
            pw = sz[0]
            scaled = image

        if scale_contain:
            k = pw / max(sz)
        else:
            k = pw / sz[0]

        sz = int(k * sz[0]), int(k * sz[1])

        x = (size - sz[0]) / 2
        y = (size - sz[1]) / 2
        res = pygame.Surface((size, size), flags=pygame.SRCALPHA)
        res.fill(background)

        if k != 1:
            scaled = pygame.transform.smoothscale(image, (sz[0], sz[1]))

        res.blit(
            scaled,
            (x + offset[0] * sz[0], y + offset[1] * sz[1])
        )

        ms = pygame.Surface((size, size), flags=pygame.SRCALPHA)
        pygame.draw.rect(ms, (255, 255, 255), pygame.Rect(0, 0, size, size), border_radius=border_radius)
        mask = pygame.mask.from_surface(ms)
        mask.to_surface(res, res, unsetcolor=(0, 0, 0, 0))
        pygame.draw.rect(res, border, pygame.Rect(0, 0, size, size), 3, border_radius=border_radius)

        return res

    def _get_icon(self, size=55, offset=(0, 0), background=(100, 150, 100), border=(50, 110, 50),
                  animation_name: str = None, border_radius=16, angle=0, scale_contain=False):

        if isinstance(self, Sprite):
            if animation_name is None:
                animation_name = self.state.animation

            if not animation_name:
                ani = self.curr_animation()
            else:
                ani = self.animations.get(animation_name)
                if not ani:
                    ani = self.curr_animation()

            img = ani.get_image(0)
            pos = self.transform.pos
            self.transform.pos = self.get_size() * 0.5
            for ch in self.get_children(True):
                ch.draw(img)

            self.transform.pos = pos

            # if hasattr(self, "front_object") and self.front_object:
            #     img = img.copy()
            #     img.blit(self.front_object.curr_animation().get_image(0), (0, 0))

            return Iconable.create_icon_image(img, size, offset, background, border, border_radius, angle,
                                              scale_contain)

        else:
            raise Exception("use Iconable as mixin for Sprite class only")


class IconableSprite(Iconable, Sprite):
    def def_icon_args(self):
        self._icon_args = {
            "border": (200, 200, 255),
            "background": (180, 180, 220)
        }
        return self
