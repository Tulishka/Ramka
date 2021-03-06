from typing import List

import pygame

Vector = pygame.Vector2

Rect = pygame.Rect


varianti_upravleniya = [
    {
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
    },
    {
        'up': pygame.K_w,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
    }
]


Poly = List[Vector]