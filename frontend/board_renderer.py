from __future__ import annotations
import pygame
import math as m
from typing import TYPE_CHECKING

from engine.board import Board
from frontend.assets import AssetManager
from engine.constants import CellType, PieceType, GameState

if TYPE_CHECKING:
    from engine.game import Game


class BoardRenderer:
    """ Handles the rendering of the board.
    """
    def __init__(self, board: Board, screen: pygame.Surface, hex_radius: int, assets: AssetManager) -> None:
        self.board = board
        self.screen = screen
        self.hex_radius = hex_radius
        self.assets = assets
        # Offset to center the board on the screen, while leaving 300 on the right for the menu
        self.x_offset = (self.screen.get_width() - 300) // 2
        self.y_offset = self.screen.get_height() // 2

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
    
    def draw_board(self, game: Game):
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
            if game.selected_cell and cell == game.selected_cell:
                # Draw a thick green outline to show it is selected
                pygame.draw.polygon(self.screen, (0, 255, 0), vertices, width=5)
            elif game.last_move and cell in game.last_move:
                # Draw a thick orange outline to show the last move
                pygame.draw.polygon(self.screen, (255, 165, 0), vertices, width=5)
            else:
                # Draw black=(0, 0, 0) outline
                pygame.draw.polygon(self.screen, (0, 0, 0), vertices, width=2)

            # Draw piece if there is one
            if cell.piece:
                color = self.assets.get_color(cell.piece.army)
                if cell.piece.piece_type == PieceType.KING:
                    if game.game_state == GameState.CHECK and cell.piece.army == game.current_turn:
                        pygame.draw.polygon(self.screen, (255, 0, 0), vertices, width=5)
                    symbol = self.assets.symbols[PieceType.KING] + self.assets.symbols[cell.piece.flavor]
                else:
                    symbol = self.assets.symbols[cell.piece.flavor]
                
                pygame.draw.circle(self.screen, color, (x, y), self.hex_radius * 0.7)
                text_surface = self.assets.font.render(symbol, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(x, y))
                self.screen.blit(text_surface, text_rect)