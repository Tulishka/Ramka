from game_manager import GameManager
from ramka import Game

Game.init('TocaBoca')
Game.цветФона = 250, 250, 250

GameManager.init()
GameManager.prepare_scene("scene1")

Game.run()
