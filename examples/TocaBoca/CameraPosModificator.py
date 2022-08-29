from ramka import Game


class CameraPosModInterface:

    def get_scroll_speed(self) -> float:
        return 700

    def get_scroll_activation_edge_range(self) -> float:
        return Game.ширинаЭкрана * 0.05
