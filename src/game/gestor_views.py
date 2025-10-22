class GestorViews:
    def __init__(self, screen, config):
        self.current_scene = None
        self.screen = screen
        self.config = config

    def cambiar_escena(self, new_scene):
        self.current_scene = new_scene
        self.current_scene.start()

    def handle_events(self, events):
        if self.current_scene:
            self.current_scene.handle_events(events)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)
