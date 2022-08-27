import pygame

from ramka import GameObject


class Circle(GameObject):
    def __init__(self, radius, color=(255, 255, 255), width=0):
        super().__init__()

        self.radius = radius
        self.color = color
        self.width = width

    def draw(self, dest: pygame.Surface):
        super().draw(dest)

        pygame.draw.circle(dest, self.color, self.screen_pos(), self.radius, self.width)
