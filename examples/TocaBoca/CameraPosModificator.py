from ramka import Game, Vector


class CameraPosModInterface:

    def get_camera_max_speed(self) -> float:
        return 700

    def get_camera_scroll_activation_edge_range(self) -> float:
        return Game.ширинаЭкрана * 0.05

    def update_camera_speed(self, cur_spd: Vector) -> Vector:
        return cur_spd
