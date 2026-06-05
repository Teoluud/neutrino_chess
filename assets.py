import pygame
from piece import Army, PieceType, Flavor


class AssetManager:
    def __init__(self) -> None:
        # Pygame requires the font module to be initialized first
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.font = pygame.font.SysFont(None, 24)

        # Dictionary mapping armies to their specific background colors
        self.colors = {
            Army.NEUTRINO: (255, 200, 0),       # Yellow
            Army.ANTI_NEUTRINO: (150, 50, 150), # Purple
        }

        # Mapping pieces to text characters for the placeholders
        self.symbols = {
            PieceType.KING: "K",
            Flavor.ELECTRONIC: "e",
            Flavor.MUONIC: "μ",
            Flavor.TAUONIC: "τ"
        }
    
    def get_color(self, army: Army) -> tuple[int, int, int]:
        """ Returns the specific RGB color for an Army.
        """
        return self.colors.get(army, (255, 255, 255))