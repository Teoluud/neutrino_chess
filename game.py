from board import Board, Cell
from rules import RulesEngine
from constants import Army, Flavor, GameState


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.rules = RulesEngine(self.board)
        self.current_turn = Army.NEUTRINO
        self.selected_cell = None

        # State variables
        self.needs_flavor_choice = False
        self.pending_move_target = None
        self.game_state = GameState.PLAYING

    def handle_click(self, q: int, r: int):
        """ Processes a mouse click at screen coordinates (x, y).
        """
        # Safety check: did the player click outside the game board?
        if (q, r) not in self.board.cells:
            self.selected_cell = None
            return
        
        clicked_cell = self.board.cells[(q, r)]

        if self.selected_cell is None:
            if clicked_cell.piece:
                # Ensure the player is selecting their own army
                if clicked_cell.piece.army == self.current_turn:
                    self.selected_cell = clicked_cell
                    print(f"Selected: {clicked_cell.piece.army.name} at ({q}, {r})")
        else:
            # A piece is already selected. Is the player trying to move or select a different piece?
            if clicked_cell.piece and clicked_cell.piece.army == self.current_turn:
                self.selected_cell = clicked_cell
                print(f"Switched selection to: ({q}, {r})")
            else:
                self._attempt_move(clicked_cell)

    def _is_legal_move(self, start_cell: Cell, target_cell: Cell) -> bool:
        """ Checks if there is a piece on the start cell and runs the piece's move validation.
        """
        if not start_cell.piece:
            return False
        if not start_cell.piece.is_valid_move(start_cell, target_cell, self.board):
            return False
        return self.rules.is_move_safe_for_king(start_cell, target_cell, self.current_turn)

    def _attempt_move(self, target_cell: Cell):
        """ Validates and executes a move to the target cell.
        """
        if self.selected_cell is not None and self._is_legal_move(self.selected_cell, target_cell):
            piece = self.selected_cell.piece
            if piece is not None:
                distance = piece._get_distance(self.selected_cell, target_cell)
                
                # Check for the Long-Range Electronic oscillation
                if piece.flavor == Flavor.ELECTRONIC and distance == 2:
                    if target_cell.piece:
                        self._execute_move(target_cell, distance, target_cell.piece.flavor)
                        return
                    else:
                        self.pending_move_target = target_cell
                        self.needs_flavor_choice = True
                        return
                # If no choice is needed, execute the move normally
                self._execute_move(target_cell, distance)
            else:
                print("Illegal move!")
                self.selected_cell = None

    def resolve_flavor_choice(self, chosen_flavor: Flavor):
        """ Called by the GUI when the player chooses the flavor.
        """
        self.needs_flavor_choice = False
        if self.selected_cell is not None and self.selected_cell.piece is not None and self.pending_move_target is not None:
            distance = self.selected_cell.piece._get_distance(self.selected_cell, self.pending_move_target)

            self._execute_move(self.pending_move_target, distance, chosen_flavor)
            self.pending_move_target = None
    
    def _execute_move(self, target_cell, distance, chosen_flavor=None):
        """ Finalizes the move, handles oscillation, and passes the turn.
        """
        if self.selected_cell is not None:
            piece_to_move = self.selected_cell.piece
            if piece_to_move is not None:
                piece_to_move.oscillate(distance, chosen_flavor)
                # Move the piece on the board
                self.selected_cell.piece = None
                target_cell.piece = piece_to_move

                # Pass the turn
                if self.current_turn == Army.NEUTRINO:
                    self.current_turn = Army.ANTI_NEUTRINO
                else:
                    self.current_turn = Army.NEUTRINO
                
                self.selected_cell = None
                if self.rules.is_checkmate(self.current_turn):
                    self.game_state = GameState.CHECKMATE
                elif self.rules.is_in_check(self.current_turn):
                    self.game_state = GameState.CHECK
                else:
                    self.game_state = GameState.PLAYING
                print(f"Move successful. It is now {self.current_turn.name}'s turn.")