from board import Board, Cell
from rules import RulesEngine
from constants import Army, Flavor, GameState, InteractionState


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.rules = RulesEngine(self.board)
        self.current_turn = Army.NEUTRINO

        self.selected_cell = None
        self.pending_move_target = None

        self.game_state = GameState.PLAYING
        self.interaction_state = InteractionState.SELECTING_PIECE

    def handle_click(self, q: int, r: int):
        """ Processes a mouse click at screen coordinates (x, y).
        """
        # Ignore board clicks while waiting for the flavor menu
        if self.interaction_state == InteractionState.AWAITING_FLAVOR:
            return
        
        # Safety check: did the player click outside the game board?
        if (q, r) not in self.board.cells:
            self.selected_cell = None
            return
        
        clicked_cell = self.board.cells[(q, r)]

        if self.interaction_state == InteractionState.SELECTING_PIECE:
            if clicked_cell.piece and clicked_cell.piece.army == self.current_turn:
                self.selected_cell = clicked_cell
                self.interaction_state = InteractionState.SELECTING_TARGET
                print(f"Selected: {clicked_cell.piece.army.name} at ({q}, {r})")

        elif self.interaction_state == InteractionState.SELECTING_TARGET:
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

    def _attempt_move(self, target_cell: Cell) -> None:
        """ Validates and executes a move to the target cell.
        """
        if self.selected_cell and self._is_legal_move(self.selected_cell, target_cell):
            piece = self.selected_cell.piece
            if piece:
                distance = piece._get_distance(self.selected_cell, target_cell)
                
                # Check for the Long-Range Electronic oscillation
                if len(piece.calculate_target_flavor(distance)) > 1:
                    if target_cell.piece:
                        self._execute_move(target_cell, distance, target_cell.piece.flavor)
                        return
                    self.pending_move_target = target_cell
                    self.interaction_state = InteractionState.AWAITING_FLAVOR
                    return
                # If no choice is needed, execute the move normally
                self._execute_move(target_cell, distance)
            else:
                print("Illegal move!")
                self.selected_cell = None
                self.interaction_state = InteractionState.SELECTING_PIECE

    def resolve_flavor_choice(self, chosen_flavor: Flavor) -> None:
        """ Called by the GUI when the player chooses the flavor.
        """
        if self.interaction_state == InteractionState.AWAITING_FLAVOR:
            if self.selected_cell and self.selected_cell.piece and self.pending_move_target:
                distance = self.selected_cell.piece._get_distance(self.selected_cell, self.pending_move_target)

                self._execute_move(self.pending_move_target, distance, chosen_flavor)
                self.pending_move_target = None
    
    def _execute_move(self, target_cell, distance, chosen_flavor=None):
        """ Finalizes the move, handles oscillation, and passes the turn.
        """
        if self.selected_cell:
            piece_to_move = self.selected_cell.piece
            if piece_to_move:
                piece_to_move.oscillate(distance, chosen_flavor)
                # Move the piece on the board
                self.selected_cell.piece = None
                target_cell.piece = piece_to_move

                # Pass the turn
                self.current_turn = Army.ANTI_NEUTRINO if self.current_turn == Army.NEUTRINO else Army.NEUTRINO
                
                self.selected_cell = None
                self.interaction_state = InteractionState.SELECTING_PIECE

                if self.rules.is_checkmate(self.current_turn):
                    self.game_state = GameState.CHECKMATE
                elif self.rules.is_in_check(self.current_turn):
                    self.game_state = GameState.CHECK
                else:
                    self.game_state = GameState.PLAYING
                print(f"Move successful. It is now {self.current_turn.name}'s turn.")

    def get_opponent(self) -> Army:
        """ Returns the opponent of the current_turn player.
        """
        if self.current_turn == Army.NEUTRINO:
            return Army.ANTI_NEUTRINO
        elif self.current_turn == Army.ANTI_NEUTRINO:
            return Army.NEUTRINO
        else:
            raise ValueError(f"{self.current_turn} is not a valid army!")