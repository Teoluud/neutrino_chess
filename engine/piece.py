from __future__ import annotations
from typing import TYPE_CHECKING

from engine.constants import Army, PieceType, Flavor, CellType

if TYPE_CHECKING:
    from engine.board import Cell, Board


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
        possible_flavors = self.calculate_target_flavor(distance)
        if len(possible_flavors) == 1:
            self.flavor = possible_flavors[0]
        elif len(possible_flavors) > 1 and new_flavor in possible_flavors:
            self.flavor = new_flavor
        else:
            raise ValueError
    
    def _get_distance(self, start_cell: Cell, target_cell: Cell) -> int:
        """ Calculates the absolute 3D hex distance between two cells.
        """
        dq = abs(start_cell.q - target_cell.q)
        dr = abs(start_cell.r - target_cell.r)
        ds = abs(start_cell.s - target_cell.s)

        return max(dq, dr, ds)
    
    def is_valid_move(self, start_cell: Cell, target_cell: Cell) -> bool:
        """ Base validation that all pieces must pass.
        """
        distance = self._get_distance(start_cell, target_cell)
        if distance not in (1, 2):
            return False
        # Can only move forward from DEPLOYMENT/KING cells
        if start_cell.cell_type == CellType.DEPLOYMENT or start_cell.cell_type == CellType.KING:
            if self.army == Army.NEUTRINO and target_cell.q >= start_cell.q:
                return False
            if self.army == Army.ANTI_NEUTRINO and target_cell.q <= start_cell.q:
                return False
        # Cannot move from DEPLOYMENT to KING cell
        if start_cell.cell_type == CellType.DEPLOYMENT and target_cell.cell_type == CellType.KING:
            return False
        # Cannot move from BATTLE to DEPLOYMENT/KING cell
        if start_cell.cell_type == CellType.BATTLE and (target_cell.cell_type == CellType.DEPLOYMENT or target_cell.cell_type == CellType.KING):
            if target_cell.piece and target_cell.piece.piece_type == PieceType.KING:
                pass # Allow the move to proceed to the check logic
            else:
                return False
        if target_cell.piece:
            # Check if there's own piece
            if target_cell.piece.army == self.army:
                return False
            # Capturing conditions
            if target_cell.piece.flavor not in self.calculate_target_flavor(distance):
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
        # Long range
        elif distance == 2:
            match self.flavor:
                case Flavor.ELECTRONIC:
                    possible_flavors.append(Flavor.MUONIC)
                    possible_flavors.append(Flavor.TAUONIC)
                case Flavor.MUONIC | Flavor.TAUONIC:
                    possible_flavors.append(Flavor.ELECTRONIC)
                case _:
                    raise ValueError("Flavor not recognized!")

        return possible_flavors
    

class King(Piece):
    def __init__(self, army: Army, piece_type: PieceType, flavor: Flavor) -> None:
        super().__init__(army, piece_type, flavor)

    def is_valid_move(self, start_cell: Cell, target_cell: Cell) -> bool:
        # Kings cannot capture
        if target_cell.piece and target_cell.piece.piece_type != PieceType.KING:
            return False
        return super().is_valid_move(start_cell, target_cell)