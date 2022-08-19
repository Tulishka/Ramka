from random import random
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import pygame

from examples.Components.PathMovingComponent import PathMovingComponent
from ramka import Game, Sprite, Vector, GameObject, Input, Component

Game.init('path finder')
Game.цветФона = 186, 184, 108


class Bot(Sprite):
    def __init__(self):
        super().__init__("pet.png")
        self.mover = PathMovingComponent(self)
        self.add_component(self.mover)


class Labirint(GameObject):
    def __init__(self):
        super().__init__()
        self.width = 10
        self.height = 6
        self.cell_size = Vector(Game.ширинаЭкрана / self.width, Game.высотаЭкрана / self.height)
        self.matrix = [[0 if random() < 0.3 else 1 for x in range(self.width)] for y in range(self.height)]

    def coord_to_screen(self, matrix_coord: Vector) -> Vector:
        return matrix_coord * self.cell_size.elementwise() + 0.5 * self.cell_size

    def coord_from_screen(self, screen_coord: Vector) -> tuple:
        dx = int(screen_coord.x / self.cell_size.x)
        dy = int(screen_coord.y / self.cell_size.y)

        return (dx, dy)

    def resolve_path(self, start, end, screen_coords=True):

        grid = Grid(matrix=self.matrix)

        start = grid.node(*start)
        end = grid.node(*end)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, _ = finder.find_path(start, end, grid)

        if screen_coords:
            for i, p in enumerate(path):
                path[i] = self.coord_to_screen(Vector(p)) + Vector(self.cell_size.x * 0.1, 0).rotate(random() * 360)

        return path

    def draw(self, dest: pygame.Surface):
        for y, row in enumerate(self.matrix):
            for x, znach in enumerate(row):
                if not znach:
                    pygame.draw.rect(dest, (100, 100, 100),
                                     pygame.Rect(Vector(x * self.cell_size.x, y * self.cell_size.y), self.cell_size))


class Ubozhistvo(GameObject):
    def __init__(self, labirint, bot):
        super().__init__()
        self.labrint: Labirint = labirint
        self.bot: Bot = bot

    @Game.on_mouse_down(button=1, hover=False)
    def mouse_down(self):
        end = self.labrint.coord_from_screen(Input.mouse_pos)
        start = self.labrint.coord_from_screen(self.bot.transform.pos)
        if end != start:
            pp = self.labrint.resolve_path(start, end)
            if pp:
                pp[-1] = Input.mouse_pos
                self.bot.mover.set_path(pp[1:])
        else:
            self.bot.mover.set_path([Input.mouse_pos])


b = Bot()
b.transform.xy = 500, 500
Game.add_object(b)

labr = Labirint()
Game.add_object(labr)

ubozhistvo = Ubozhistvo(labr, b)
Game.add_object(ubozhistvo)

Game.run()
