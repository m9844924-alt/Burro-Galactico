import pygame
import sys

from ui.main_view import MainView


def main():
    """Main entry point for Burro Galáctico"""
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Burro Galáctico - Sistema de Navegación Estelar")
    
    clock = pygame.time.Clock()
    
    # Create main view
    main_view = MainView(screen)
    
    # Main game loop
    while True:
        # Get events
        events = pygame.event.get()
        
        # Check for quit
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        
        # Update and draw
        main_view.handle_events(events)
        main_view.update()
        main_view.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()