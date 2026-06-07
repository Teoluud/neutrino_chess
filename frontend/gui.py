import math as m
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from frontend.assets import AssetManager
from frontend.ui import Button, UIManager
from frontend.board_renderer import BoardRenderer
from engine.game import Game
from engine.constants import Flavor, GameState, InteractionState


class NeutrinoGUI:
    """ Handles the GUI for the game.
    """
    def __init__(self, game: Game, hex_radius: int = 50) -> None:
        self.game = game
        self.board = self.game.board
        self.hex_radius = hex_radius
        self.assets = AssetManager()
        self.ui_manager = UIManager()

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

    def draw_valid_moves(self, valid_cells: list) -> None:
        """ Draws a green circle on the valid moves cells for a selected piece.
        """
        for cell in valid_cells:
            x, y = self.board_renderer.axial_to_pixel(cell.q, cell.r)
            pygame.draw.circle(self.screen, (0, 255, 0), (int(x), int(y)), self.hex_radius * 0.8, width=2)

    def run(self):
        """ Main game loop.
        """
        clock = pygame.time.Clock()
        running = True
        while running:
            if self.game.game_state == GameState.CHECKMATE:
                running = False
                print(f"Checkmate! {self.game.get_opponent().name} won!")
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Check for mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is the left mouse button
                        if self.game.interaction_state == InteractionState.AWAITING_FLAVOR:
                            flavor = self.ui_manager.handle_click(event.pos)
                            if flavor:
                                self.game.resolve_flavor_choice(flavor)
                        
                        else:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            q, r = self.board_renderer.pixel_to_axial(mouse_x, mouse_y)
                            self.game.handle_click(q, r)
            
            self.screen.fill((255, 255, 255)) # White background
            self.board_renderer.draw_board(self.game)

            if self.game.interaction_state == InteractionState.AWAITING_FLAVOR:
                self.draw_flavor_menu()
            
            if self.game.interaction_state == InteractionState.SELECTING_TARGET and self.game.valid_cells:
                self.draw_valid_moves(self.game.valid_cells)
            
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()