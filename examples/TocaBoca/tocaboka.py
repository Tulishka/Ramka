from game_manager import GameManager
from ramka import Game

Game.init('TocaBoca', fullscreen=True)
Game.цветФона = 250, 250, 250

GameManager.init()

GameManager.prepare_scene("game1")

Game.run()

# todo: закладки в меню вещей (Персонажи, интерьер, вещи, транспорт)
# todo: объект локация
# todo: выбор локации / переход между локациями
# todo: particle generator


