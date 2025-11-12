"""
Galactic Donkey - Main Application Entry Point
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import pygame

from src.config import display
from src.presentation.views.main_view import MainView


def main():
    """Main application entry point"""

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((display.WINDOW_WIDTH, display.WINDOW_HEIGHT))
    pygame.display.set_caption(display.TITLE)

    clock = pygame.time.Clock()

    main_view = MainView(screen)

    running = True
    while running:

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        main_view.handle_events(events)
        main_view.update()

        main_view.draw(screen)

        pygame.display.flip()
        clock.tick(display.FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

