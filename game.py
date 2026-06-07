from board import Board, Cell
from rules import RulesEngine
from constants import Army, Flavor, GameState, InteractionState


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.rules = RulesEngine(self.board)
        self.current_turn = Army.NEUTRINO

        self.selected_cell = None
        self.valid_cells = None
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
            self.valid_cells = None
            return
        
        clicked_cell = self.board.cells[(q, r)]

        if self.interaction_state == InteractionState.SELECTING_PIECE:
            self._handle_piece_selection(clicked_cell)

        elif self.interaction_state == InteractionState.SELECTING_TARGET:
            self._handle_target_selection(clicked_cell)

    def _handle_piece_selection(self, clicked_cell: Cell) -> None:
        """ Handles the piece selection (when the state is SELECTING_PIECE).
        """
        if clicked_cell.piece and clicked_cell.piece.army == self.current_turn:
                self.selected_cell = clicked_cell
                self.valid_cells = [cell for cell in self.board.cells.values() if self._is_legal_move(self.selected_cell, cell)]
                self.interaction_state = InteractionState.SELECTING_TARGET
                print(f"Selected: {clicked_cell.piece.army.name} at ({clicked_cell.q}, {clicked_cell.r})")
    
    def _handle_target_selection(self, clicked_cell: Cell) -> None:
        """ Handles the target selection:
        - Selects a new piece if it's an allied one
        - Attemps to move otherwise
        """
        # A piece is already selected. Is the player trying to move or select a different piece?
        if clicked_cell.piece and clicked_cell.piece.army == self.current_turn:
            self.selected_cell = clicked_cell
            self.valid_cells = [cell for cell in self.board.cells.values() if self._is_legal_move(self.selected_cell, cell)]
            print(f"Switched selection to: ({clicked_cell.q}, {clicked_cell.r})")
        else:
            self._attempt_move(clicked_cell)

    def _is_legal_move(self, start_cell: Cell, target_cell: Cell) -> bool:
        """ Checks if there is a piece on the start cell and runs the piece's move validation.
        """
        if not start_cell.piece:
            return False
        if not start_cell.piece.is_valid_move(start_cell, target_cell):
            return False
        if not self.rules.get_safe_flavors(start_cell, target_cell, self.current_turn):
            return False
        return True

    def _attempt_move(self, target_cell: Cell) -> None:
        """ Validates and executes a move to the target cell.
        """
        if self.selected_cell and self._is_legal_move(self.selected_cell, target_cell):
            piece = self.selected_cell.piece
            if piece:
                distance = piece._get_distance(self.selected_cell, target_cell)
                
                # Get the list of safe flavors
                safe_flavors = self.rules.get_safe_flavors(self.selected_cell, target_cell, self.current_turn)
                
                # Check if we need the player to choose
                if len(safe_flavors) > 1:
                    if target_cell.piece:
                        self._execute_move(target_cell, distance, target_cell.piece.flavor)
                        return
                    self.pending_move_target = target_cell
                    self.interaction_state = InteractionState.AWAITING_FLAVOR
                    return
                # If no choice is needed, execute the move normally
                self._execute_move(target_cell, distance, safe_flavors[0])
            else:
                print("Illegal move!")
                self.selected_cell = None
                self.valid_cells = None
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
                self.valid_cells = None
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
        



