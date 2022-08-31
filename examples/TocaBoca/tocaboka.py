from game_manager import GameManager
from ramka import Game

Game.init('TocaBoca', fullscreen=True)
Game.цветФона = 250, 250, 250

GameManager.init()

GameManager.prepare_scene("game1")

Game.run()
