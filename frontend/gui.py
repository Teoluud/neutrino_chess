import math as m
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from frontend.assets import AssetManager
from frontend.ui import Button, UIManager
from frontend.board_renderer import BoardRenderer
from engine.game import Game
from engine.constants import Flavor, Army, GameState, InteractionState


class NeutrinoGUI:
    """ Handles the GUI for the game.
    """
    def __init__(self, game: Game, hex_radius: int = 45) -> None:
        self.game = game
        self.board = self.game.board
        self.hex_radius = hex_radius
        self.assets = AssetManager()
        self.ui_manager = UIManager()
        self.endgame_ui = UIManager()

        # Pygame initialization
        pygame.init()
        self.width = 1000
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Neutrino Chess")

        self.board_renderer = BoardRenderer(self.board, self.screen, self.hex_radius, self.assets)

        center_x = self.width // 2
        center_y = self.height // 2
        # Pop-up menu buttons
        self.btn_mu = Button(
            dimensions=(center_x - 120, center_y - 50, 100, 100),
            color=(200, 200, 200),
            text=self.assets.font.render(self.assets.symbols[Flavor.MUONIC], True, (0, 0, 0)),
            data=Flavor.MUONIC)
        self.btn_tau = Button(
            dimensions=(center_x + 20, center_y - 50, 100, 100),
            color=(200, 200, 200),
            text=self.assets.font.render(self.assets.symbols[Flavor.TAUONIC], True, (0, 0, 0)),
            data=Flavor.TAUONIC)
        self.ui_manager.buttons.append(self.btn_mu)
        self.ui_manager.buttons.append(self.btn_tau)

        # Engame buttons
        self.play_again_btn = Button(
            dimensions=(center_x - 200, center_y - 50, 400, 100),
            color=(200, 200, 200),
            text=self.assets.font.render("Play Again", True, (0, 0, 0)),
            data="RESTART"
        )
        self.endgame_ui.buttons.append(self.play_again_btn)

    def draw_flavor_menu(self):
        """ Draws a semi-transparent overlay and flavor selection buttons.
        """
        # Draw a semi-transparent white overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))

        self.ui_manager.draw_all(self.screen)

        # Draw the prompt text
        prompt = self.assets.font.render("Long Range Jump! Choose new flavor:", True, (0, 0, 0))
        self.screen.blit(prompt, prompt.get_rect(center=(self.width//2, self.height//2 - 80)))

    def draw_endgame_menu(self):
        """ Draws the endgame menu.
        """
        # Draw a semi-transparent white overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))

        self.endgame_ui.draw_all(self.screen)

        # Draw the prompt text
        prompt = self.assets.font.render(f"CHECKMATE! {self.game.get_opponent().name} won!", True, (0, 0, 0))
        self.screen.blit(prompt, prompt.get_rect(center=(self.width//2, self.height//2 - 80)))

    def draw_valid_moves(self, valid_cells: list) -> None:
        """ Draws a green circle on the valid moves cells for a selected piece.
        """
        for cell in valid_cells:
            x, y = self.board_renderer.axial_to_pixel(cell.q, cell.r)
            pygame.draw.circle(self.screen, (0, 255, 0), (int(x), int(y)), self.hex_radius * 0.8, width=2)

    def draw_captured_pieces(self):
        """ Draws the captured pieces in the right-side panel. """
        # Draw a subtle background for the side panel
        pygame.draw.rect(self.screen, (240, 240, 240), (700, 0, 300, self.height))

        # Neutrino captures at the top, Anti-neutrino captures at the bottom
        positions = {
            Army.NEUTRINO: (750, 100),
            Army.ANTI_NEUTRINO: (750, 500)
        }

        for army, (start_x, start_y) in positions.items():
            title_text = self.assets.font.render(army.name, True, (0, 0, 0))
            self.screen.blit(title_text, title_text.get_rect(center=(self.width - (300 // 2), start_y - 50)))
            for i, piece in enumerate(self.game.captured_pieces[army]):
                # Create a 3-column grid spacing them 60 pixels apart
                x = start_x + (i % 3) * 2 * self.hex_radius
                y = start_y + (i // 3) * 2 * self.hex_radius

                # Draw the piece
                color = self.assets.get_color(piece.army)
                symbol = self.assets.symbols[piece.flavor]
                pygame.draw.circle(self.screen, color, (x, y), self.hex_radius * 0.7)
                
                text_surface = self.assets.font.render(symbol, True, (0, 0, 0))
                self.screen.blit(text_surface, text_surface.get_rect(center=(x, y)))

                if piece == self.game.selected_captured_piece:
                    pygame.draw.circle(self.screen, (0, 255, 0), (x, y), self.hex_radius * 0.7, width=5)

    def run(self):
        """ Main game loop.
        """
        clock = pygame.time.Clock()
        running = True
        while running:
            if self.game.game_state == GameState.CHECKMATE and self.game.interaction_state != InteractionState.ENDGAME_MENU:
                self.game.interaction_state = InteractionState.ENDGAME_MENU
                print(f"Checkmate! {self.game.get_opponent().name} won!")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Check for mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is the left mouse button
                        # Flavor selection
                        if self.game.interaction_state == InteractionState.AWAITING_FLAVOR:
                            flavor = self.ui_manager.handle_click(event.pos)
                            if flavor:
                                self.game.resolve_flavor_choice(flavor)
                        # Endgame menu selection
                        elif self.game.interaction_state == InteractionState.ENDGAME_MENU:
                            action = self.endgame_ui.handle_click(event.pos)
                            if action == "RESTART":
                                self.game.reset()
                        else:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            if mouse_x < 700:
                                q, r = self.board_renderer.pixel_to_axial(mouse_x, mouse_y)
                                self.game.handle_click(q, r)
                            else:
                                start_x = 750
                                start_y = 100 if self.game.current_turn == Army.NEUTRINO else 500
                                
                                # Loop through the active player's captured pieces
                                for i, piece in enumerate(self.game.captured_pieces[self.game.current_turn]):
                                    # Calculate the exact center of this piece (using our drawing math)
                                    x = start_x + (i % 3) * 2 * self.hex_radius
                                    y = start_y + (i // 3) * 2 * self.hex_radius
                                    
                                    # Check if the mouse click is within the piece's circle
                                    if m.hypot(mouse_x - x, mouse_y - y) <= self.hex_radius * 0.7:
                                        print(f"Clicked on {piece.flavor.name} from the reserve!")
                                        self.game.selected_captured_piece = piece
                                        self.game.selected_cell = None
                                        self.game.valid_cells = None
                                        break # Stop checking once we find the clicked piece
            
            self.screen.fill((255, 255, 255)) # White background
            self.board_renderer.draw_board(self.game)
            self.draw_captured_pieces()

            if self.game.interaction_state == InteractionState.AWAITING_FLAVOR:
                self.draw_flavor_menu()
            
            if self.game.interaction_state == InteractionState.SELECTING_TARGET and self.game.valid_cells:
                self.draw_valid_moves(self.game.valid_cells)

            if self.game.interaction_state == InteractionState.ENDGAME_MENU:
                self.draw_endgame_menu()
            
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()