from __future__ import annotations
from typing import TYPE_CHECKING

from engine.constants import Army, PieceType, Flavor

if TYPE_CHECKING:
    from engine.board import Board, Cell
    from engine.piece import Piece


class RulesEngine:
    """ Analyzes the board state to enforce game rules.
    """
    def __init__(self, board: Board) -> None:
        self.board = board
    
    def is_in_check(self, army: Army) -> bool:
        """ Checks if the King of the given army is under threat.
        """
        king_cell = self.board.find_king(army)

        for cell in self.board.cells.values():
            piece = cell.piece

            # Identify enemy pieces
            if piece is not None and piece.army != army:
                # Check if the piece threatens the king
                if piece.is_valid_move(cell, king_cell):
                    return True
        
        return False
    
    def get_safe_flavors(self, start_cell: 'Cell', target_cell: 'Cell', current_turn: 'Army') -> list[Flavor]:
        moving_piece = start_cell.piece
        original_target_piece = target_cell.piece
        
        safe_flavors = []

        if moving_piece:
            original_flavor = moving_piece.flavor
            distance = moving_piece._get_distance(start_cell, target_cell)
            possible_flavors = moving_piece.calculate_target_flavor(distance)
        
            # Simulate the move
            target_cell.piece = moving_piece
            start_cell.piece = None
            
            # Test EVERY possible flavor
            for flavor in possible_flavors:
                target_cell.piece.oscillate(distance, flavor)
                if not self.is_in_check(current_turn):
                    safe_flavors.append(flavor) # Keep it if it's safe
                
                # Reset piece state for the next loop iteration
                target_cell.piece.flavor = original_flavor
            
            # Revert the move
            start_cell.piece = moving_piece
            target_cell.piece = original_target_piece
            start_cell.piece.flavor = original_flavor

        return safe_flavors
    
    def get_attackers(self, king_cell: Cell, army: Army) -> list[tuple[Piece, Cell]]:
        """ Returns a list of (piece, cell) that are currently threatening the king.
        """
        attackers = []
        for cell in self.board.cells.values():
            piece = cell.piece
            # Find pieces of the opposite army that can legally attack the King's square
            if piece is not None and piece.army != army:
                if piece.is_valid_move(cell, king_cell):
                    attackers.append((piece, cell))
        return attackers
    
    def is_checkmate(self, army: Army) -> bool:
        """ Determines if the current player is in checkmate.
        """
        king_cell = self.board.find_king(army)
        attackers = self.get_attackers(king_cell, army)

        if not attackers:
            return False
        
        if self.can_king_escape(king_cell, army):
            return False
        
        if len(attackers) == 1:
            attacker_piece, attacker_cell = attackers[0]
            if self.can_any_piece_capture(attacker_cell, army):
                return False
        
        return True
    
    def can_king_escape(self, king_cell: Cell, army: Army) -> bool:
        """ Checks if the King can move to any safe cell.
        """
        king_piece = king_cell.piece

        if king_piece is not None:
            for target_cell in self.board.cells.values():
                if king_piece.is_valid_move(king_cell, target_cell) and self.get_safe_flavors(king_cell, target_cell, army):
                    return True
        return False
    
    def can_any_piece_capture(self, target_cell: Cell, army: Army) -> bool:
        """ Checks if any friendly piece can move to the target_cell.
        """
        for cell in self.board.cells.values():
            piece = cell.piece
            if piece and piece.army != army and piece.piece_type != PieceType.KING:
                if piece.is_valid_move(cell, target_cell):
                    return True
        return False