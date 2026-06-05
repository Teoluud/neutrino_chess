import math as m
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from board import Board
from assets import AssetManager
from game import Game
from constants import CellType, PieceType, Flavor


class NeutrinoGUI:
    """ Handles the GUI for the game.
    """
    def __init__(self, board: Board, game: Game, hex_radius: int = 50) -> None:
        self.board = board
        self.game = game
        self.hex_radius = hex_radius
        self.assets = AssetManager()

        # Pygame initialization
        pygame.init()
        self.width = 1000
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Neutrino Chess")

        # Offset to center the board on the screen
        self.x_offset = self.width // 2
        self.y_offset = self.height // 2

        # Rectangles for pop-up menu buttons
        self.btn_mu: pygame.Rect | None = None
        self.btn_tau: pygame.Rect | None = None

    def axial_to_pixel(self, q: int, r: int) -> tuple[float, float]:
        """ Converts axial coordinates to pixel coordinates.
        """
        x = self.hex_radius * 1.5 * q
        y = self.hex_radius * m.sqrt(3) * (q/2 + r)
        return x + self.x_offset, y + self.y_offset
    
    def pixel_to_axial(self, x: float, y: float) -> tuple[int, int]:
        """ Converts x, y coordinates to hex axial coordinates.
        """
        # Remove offsets
        x -= self.x_offset
        y -= self.y_offset
        # Calculate fraction coordinates
        q_frac = x / (1.5 * self.hex_radius)
        r_frac = (y / (self.hex_radius * m.sqrt(3))) - q_frac / 2
        s_frac = -q_frac - r_frac
        # Round to nearest integer
        q = round(q_frac)
        r = round(r_frac)
        s = round(s_frac)
        # Calculate rounding differences
        q_diff = abs(q - q_frac)
        r_diff = abs(r - r_frac)
        s_diff = abs(s - s_frac)
        # Fix the coordinate with the largest error to satisfy q + r + s = 0
        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        elif r_diff > s_diff:
            r = -q - s
        
        return int(q), int(r)
    
    def _get_hex_vertices(self, x, y) -> list[tuple[float, float]]:
        """ Helper function to return hex vertices for a specific cell.
        """
        vertices = []
        for i in range(6):
            theta = m.pi/3 * i
            x_vert = x + self.hex_radius * m.cos(theta)
            y_vert = y + self.hex_radius * m.sin(theta)
            vertices.append((x_vert, y_vert))
        return vertices
    
    def draw_board(self):
        """ Draws the hexagonal board and its specific zones.
        """
        for cell in self.board.cells.values():
            # Determine cell color
            if cell.cell_type == CellType.DEPLOYMENT:
                if cell.q < 0:
                    color = (200, 150, 200) # Purple
                else:
                    color = (255, 255, 150) # Yellow
            elif cell.cell_type == CellType.KING:
                color = (200, 200, 200) # Grey
            else:
                color = (255, 255, 255) # White
            # Draw the cell
            x, y = self.axial_to_pixel(cell.q, cell.r)
            vertices = self._get_hex_vertices(x, y)
            # Fill hexagon
            pygame.draw.polygon(self.screen, color, vertices)
            # Check if cell is the one selected in the Game state
            if self.game.selected_cell and cell == self.game.selected_cell:
                # Draw a thick green outline to show it is selected
                pygame.draw.polygon(self.screen, (0, 255, 0), vertices, width=5)
            else:
                # Draw black=(0, 0, 0) outline
                pygame.draw.polygon(self.screen, (0, 0, 0), vertices, width=2)

            # Draw piece if there is one
            if cell.piece:
                color = self.assets.get_color(cell.piece.army)
                if cell.piece.piece_type == PieceType.KING:
                    symbol = self.assets.symbols[PieceType.KING] + self.assets.symbols[cell.piece.flavor]
                else:
                    symbol = self.assets.symbols[cell.piece.flavor]
                
                pygame.draw.circle(self.screen, color, (x, y), self.hex_radius * 0.7)
                text_surface = self.assets.font.render(symbol, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(x, y))
                self.screen.blit(text_surface, text_rect)

    def draw_flavor_menu(self):
        """ Draws a semi-transparent overlay and flavor selection buttons.
        """
        # Draw a semi-transparent white overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))

        center_x = self.width // 2
        center_y = self.height // 2

        # Define button sizes and positions
        self.btn_mu = pygame.Rect(center_x - 120, center_y - 50, 100, 100)
        self.btn_tau = pygame.Rect(center_x + 20, center_y - 50, 100, 100)

        # Draw the button backgrounds
        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_mu, border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_tau, border_radius=15)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_mu, width=3, border_radius=15)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_tau, width=3, border_radius=15)

        # Render the text symbols onto the buttons
        text_mu = self.assets.font.render(self.assets.symbols[Flavor.MUONIC], True, (0, 0, 0))
        text_tau = self.assets.font.render(self.assets.symbols[Flavor.TAUONIC], True, (0, 0, 0))

        self.screen.blit(text_mu, text_mu.get_rect(center=self.btn_mu.center))
        self.screen.blit(text_tau, text_tau.get_rect(center=self.btn_tau.center))

        # Draw the prompt text
        prompt = self.assets.font.render("Long Range Jump! Choose new flavor:", True, (0, 0, 0))
        self.screen.blit(prompt, prompt.get_rect(center=(center_x, center_y - 80)))

    def run(self):
        """ Main game loop.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Check for mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is the left mouse button
                        if self.game.needs_flavor_choice:
                            if self.btn_mu and self.btn_mu.collidepoint(event.pos):
                                self.game.resolve_flavor_choice(Flavor.MUONIC)
                            elif self.btn_tau and self.btn_tau.collidepoint(event.pos):
                                self.game.resolve_flavor_choice(Flavor.TAUONIC)
                        
                        else:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            q, r = self.pixel_to_axial(mouse_x, mouse_y)
                            self.game.handle_click(q, r)
            
            self.screen.fill((255, 255, 255)) # White background
            self.draw_board()

            if self.game.needs_flavor_choice:
                self.draw_flavor_menu()
            
            pygame.display.flip()
        
        pygame.quit()



