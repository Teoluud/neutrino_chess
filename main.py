from engine.game import Game
from frontend.gui import NeutrinoGUI


game = Game()
gui = NeutrinoGUI(game)
gui.run()