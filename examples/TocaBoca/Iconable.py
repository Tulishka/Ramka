import pygame

from ramka import Sprite


class Iconable:

    def get_icon(self):
        return self._get_icon()

    def _get_icon(self, size=55, offset=(0, 0), background=(100, 150, 100), border=(50, 110, 50),
                  animation_name: str = "state1", border_radius=16):

        if isinstance(self,Sprite):
            if not animation_name:
                ani = self.curr_animation()
            else:
                ani = self.animations.get(animation_name)
                if not ani:
                    ani = self.curr_animation()

            img = ani.get_image(0)

            sz = img.get_size()
            pw = size - size // 7
            k = pw / sz[0]
            x = (size - pw) / 2
            y = (size - int(k * sz[1])) / 2
            res = pygame.Surface((size, size), flags=pygame.SRCALPHA)
            res.fill(background)
            res.blit(
                pygame.transform.smoothscale(img, (pw, int(k * sz[1]))),
                (x + offset[0] * k * sz[0], y + offset[1] * k * sz[1])
            )

            ms = pygame.Surface((size, size), flags=pygame.SRCALPHA)
            pygame.draw.rect(ms, (255, 255, 255), pygame.Rect(0, 0, size, size), border_radius=border_radius)
            mask = pygame.mask.from_surface(ms)
            mask.to_surface(res, res, unsetcolor=(0, 0, 0, 0))
            pygame.draw.rect(res, border, pygame.Rect(0, 0, size, size), 3, border_radius=border_radius)

            return res
        else:
            raise Exception("use Iconable as mixin for Sprite class only")
