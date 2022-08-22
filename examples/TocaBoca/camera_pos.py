import pygame

from ramka import GameObject, Game, Input


class CameraPos(GameObject):
    def __init__(self):
        super().__init__()
        self.transform.pos = Game.screen_size * 0.5
        self.spd = 300

    def update(self, deltaTime: float):
        super(CameraPos, self).update(deltaTime)

        # mpos=camera.transform.add_to_vector(Input.mouse_pos)
        # if pygame.mouse.get_pressed(3)[0]:
        #     self.transform.move_toward_ip(Input.mouse_pos, self.spd * deltaTime,use_local=False)
