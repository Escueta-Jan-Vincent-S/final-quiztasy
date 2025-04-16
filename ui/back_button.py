import os
from .button import Button

class BackButton:
    def __init__(self, screen, script_dir, action, audio_manager=None, position=(100, 100), scale=0.5):
        """Creates a reusable Back button."""
        self.screen = screen
        self.button = Button(position[0], position[1],
                             os.path.join(script_dir, "assets", "images", "buttons", "back button", "back_btn_img.png"),
                             os.path.join(script_dir, "assets", "images", "buttons", "back button", "back_btn_hover.png"),
                             None, action, scale=scale, audio_manager=audio_manager)

    def draw(self):
        """Draws the Back button on the screen."""
        self.button.draw(self.screen)

    def update(self, event):
        """Handles updates (hover, clicks) for the Back button."""
        self.button.update(event)
