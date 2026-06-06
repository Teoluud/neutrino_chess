from __future__ import annotations
from typing import TYPE_CHECKING

from constants import Army, PieceType

if TYPE_CHECKING:
    from board import Board, Cell
    from piece import Piece


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
                if piece.is_valid_move(cell, king_cell, self.board):
                    return True
        
        return False
    
    def get_attackers(self, king_cell: Cell, army: Army) -> list[tuple[Piece, Cell]]:
        """ Returns a list of (piece, cell) that are currently threatening the king.
        """
        attackers = []
        for cell in self.board.cells.values():
            piece = cell.piece
            # Find pieces of the opposite army that can legally attack the King's square
            if piece is not None and piece.army != army:
                if piece.is_valid_move(cell, king_cell, self.board):
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
                if king_piece.is_valid_move(king_cell, target_cell, self.board):
                    original_target_piece = target_cell.piece

                    target_cell.piece = king_piece
                    king_cell.piece = None

                    attackers = self.get_attackers(target_cell, army)

                    king_cell.piece = king_piece
                    target_cell.piece = original_target_piece

                    # If no attackers found, the King can escape
                    if not attackers:
                        return True
        return False
    
    def can_any_piece_capture(self, target_cell: Cell, army: Army) -> bool:
        """ Checks if any friendly piece can move to the target_cell.
        """
        for cell in self.board.cells.values():
            piece = cell.piece
            if piece and army != army and piece.piece_type != PieceType.KING:
                if piece.is_valid_move(cell, target_cell, self.board):
                    return True
        return False