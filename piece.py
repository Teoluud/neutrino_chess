from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from board import Cell, Board


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


class Piece:
    """ Represents a single neutrino piece.
    """
    def __init__(self, army: 'Army', piece_type: 'PieceType', flavor: 'Flavor') -> None:
        self.army = army
        self.piece_type = piece_type
        self.flavor = flavor

    def oscillate(self, distance: int, new_flavor: 'Flavor | None' = None) -> None:
        """ Handles the neutrino oscillation after a move.
        """
        # Short range
        if distance == 1:
            match self.flavor:
                case Flavor.ELECTRONIC:
                    pass
                case Flavor.MUONIC:
                    self.flavor = Flavor.TAUONIC
                case Flavor.TAUONIC:
                    self.flavor = Flavor.MUONIC
                case _:
                    raise ValueError("Flavor not recognized!")
        # Long range
        elif distance == 2:
            match self.flavor:
                case Flavor.ELECTRONIC:
                    if new_flavor in (Flavor.MUONIC, Flavor.TAUONIC):
                        self.flavor = new_flavor
                    else:
                        raise ValueError(f"Can't oscillate from Electronic to {new_flavor}")
                case Flavor.MUONIC | Flavor.TAUONIC:
                    self.flavor = Flavor.ELECTRONIC
                case _:
                    raise ValueError("Flavor not recognized!")
        # Safety check
        else:
            raise ValueError("Can move only 1 or 2 cells!")
    
    def _get_distance(self, start_cell: Cell, target_cell: Cell) -> int:
        """ Calculates the absolute 3D hex distance between two cells.
        """
        dq = abs(start_cell.q - target_cell.q)
        dr = abs(start_cell.r - target_cell.r)
        ds = abs(start_cell.s - target_cell.s)

        return max(dq, dr, ds)
    
    def is_valid_move(self, start_cell: Cell, target_cell: Cell, board: Board) -> bool:
        """ Base validation that all pieces must pass.
        """
        distance = self._get_distance(start_cell, target_cell)
        if distance not in (1, 2):
            return False
        if target_cell.piece:
            if target_cell.piece.army == self.army:
                return False
            
        return True
    
    def calculate_target_flavor(self, distance: int) -> list['Flavor']:
        """ Returns a list of possible flavors after moving the given distance.
        """
        possible_flavors = []
        # Short range
        if distance == 1:
            match self.flavor:
                case Flavor.ELECTRONIC:
                    possible_flavors.append(Flavor.ELECTRONIC)
                case Flavor.MUONIC:
                    possible_flavors.append(Flavor.TAUONIC)
                case Flavor.TAUONIC:
                    possible_flavors.append(Flavor.MUONIC)
                case _:
                    raise ValueError("Flavor not recognized!")
                
        return possible_flavors