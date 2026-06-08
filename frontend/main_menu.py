import pygame

from frontend.assets import AssetManager
from frontend.ui import Button, UIManager

class MainMenu:
    """ Handles the main menu and then hands it over to the GUI.
    """
    def __init__(self) -> None:
        self.assets = AssetManager()
        self.menu_manager = UIManager()

        pygame.init()
        self.width = 1000
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Neutrino Chess")

        center_x = self.width // 2
        center_y = self.height // 2

        btn_dims = (400, 100)
        self.start_btn = Button(
            dimensions=(center_x - btn_dims[0] // 2, center_y - btn_dims[1] // 2, btn_dims[0], btn_dims[1]),
            color=(200, 200, 200),
            text=self.assets.font.render("Start Game", True, (0, 0, 0)),
            data="START"
        )
        self.menu_manager.buttons.append(self.start_btn)

    def run(self) -> None:
        """ Main menu loop.
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Check for mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is the left mouse button
                        action = self.menu_manager.handle_click(event.pos)
                        if action == "START":
                            print("Starting Game...")
                            running = False

            self.screen.fill((255, 255, 255)) # White background
            self.menu_manager.draw_all(self.screen)
            pygame.display.flip()
            clock.tick(60)

    