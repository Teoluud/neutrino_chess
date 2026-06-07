from enum import Enum


class CellType(Enum):
    """ Enum representing the distinct functional zones on the board.
    """
    KING = 0
    DEPLOYMENT = 1
    BATTLE = 2


class Army(Enum):
    NEUTRINO = 0
    ANTI_NEUTRINO = 1


class PieceType(Enum):
    REGULAR = 0
    KING = 1


class Flavor(Enum):
    ELECTRONIC = 0
    MUONIC = 1
    TAUONIC = 2


class GameState(Enum):
    PLAYING = 0
    CHECK = 1
    CHECKMATE = 2


class InteractionState(Enum):
    SELECTING_PIECE = 0
    SELECTING_TARGET = 1
    AWAITING_FLAVOR = 2
    ENDGAME_MENU = 3