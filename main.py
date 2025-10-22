import pygame, sys, json
from src.game.gestor_views import GestorViews


def main():
    pygame.init()
    
    pygame.display.set_caption("Burro Galáctico")
    
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1280, 720))
    
    manager = GestorViews(screen, {})

    while True:
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # manager.handle_events(events)
        manager.update()
        manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()