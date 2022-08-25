import pygame

from examples.Components.DragAndDrop import Draggable
from base_item import BaseItem


class Interier(Draggable,BaseItem):
    def __init__(self, *a, **b):
        super(Interier, self).__init__(*a, **b)

    def on_drag_start(self):
        return bool(pygame.key.get_mods() & pygame.KMOD_LSHIFT)
