from game_manager import GameManager
from ramka import Game

Game.init('TocaBoca', fullscreen=0)
Game.цветФона = 250, 250, 250

GameManager.init()
GameManager.prepare_scene("game")

Game.run()
