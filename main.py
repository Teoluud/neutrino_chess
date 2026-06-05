from board import Board
from game import Game
from gui import NeutrinoGUI

board = Board()
game = Game(board)
gui = NeutrinoGUI(board, game)
gui.run()