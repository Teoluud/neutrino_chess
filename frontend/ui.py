from typing import Any

import pygame

class Button:
    def __init__(self, dimensions: tuple, color: tuple, text: pygame.Surface, data: Any = None) -> None:
        self.rect = pygame.Rect(dimensions)
        self.color = color
        self.text = text
        self.data = data

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        """ Checks if the button is clicked.
        """
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        """ Draws the button.
        """
        pygame.draw.rect(screen, self.color, self.rect, border_radius=15)
        screen.blit(self.text, self.text.get_rect(center=self.rect.center))


class UIManager:
    def __init__(self) -> None:
        self.buttons = []

    def draw_all(self, screen: pygame.Surface) -> None:
        for button in self.buttons:
            button.draw(screen)

    def handle_click(self, mouse_pos: tuple[int, int]) -> Any | None:
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                return button.data
        return None