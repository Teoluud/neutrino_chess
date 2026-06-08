from frontend.main_menu import MainMenu
from frontend.gui import NeutrinoGUI
from engine.game import Game


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
    
    game = Game()
    gui = NeutrinoGUI(game)
    gui.run()