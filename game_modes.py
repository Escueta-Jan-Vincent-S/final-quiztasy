import pygame
import os
from button import Button
from back_button import BackButton

class GameModes:
    def __init__(self, screen, audio_manager, script_dir, scale=0.5, game_instance=None):
        self.game_instance = game_instance  # Store the game instance
        self.screen = screen
        self.audio_manager = audio_manager
        self.visible = False  # Controls visibility
        self.scale = scale  # Scaling factor for buttons

        # Define button positions
        self.positions = {
            "sp": (960, 280),  # Middle top
            "pvp": (480, 800),  # Bottom left
            "custom": (1440, 800)  # Bottom right
        }

        # Load buttons with scaling
        self.buttons = {
            "sp": self.create_button(script_dir, "sp", self.positions["sp"]),
            "pvp": self.create_button(script_dir, "pvp", self.positions["pvp"]),
            "custom": self.create_button(script_dir, "custom", self.positions["custom"])
        }

        # Add Back button
        self.back_button = BackButton(self.screen, script_dir, self.go_back, audio_manager=self.audio_manager, position=(100, 100), scale=0.25)

    def play_single_player(self):
        print("Playing single-player mode")
        if self.game_instance:
            # Check if game_instance is MainMenu or FinalQuiztasy
            if hasattr(self.game_instance, 'hero_selection'):
                # Direct access to hero_selection
                self.game_instance.hero_selection.show()
            elif hasattr(self.game_instance, 'game_instance') and hasattr(self.game_instance.game_instance,'hero_selection'):
                # Access through MainMenu's game_instance
                self.game_instance.game_instance.hero_selection.show()

    def create_button(self, script_dir, name, position):
        """Helper method to create buttons with scaling."""
        img_path = os.path.join(script_dir, "images", "buttons", "game modes", "modes", f"{name}_btn_img.png")
        hover_path = os.path.join(script_dir, "images", "buttons", "game modes", "modes", f"{name}_btn_hover.png")

        return Button(
            position[0], position[1], img_path, hover_path, None,
            lambda: self.on_click(name), scale=self.scale, audio_manager=self.audio_manager
        )

    def on_click(self, name):
        """Handles button clicks for game mode selection."""
        print(f"Button {name} clicked!")  # ✅ Debugging
        if name == "sp":
            self.play_single_player()

    def go_back(self):
        """Handles Back button click."""
        print("Back button clicked!")
        self.hide()  # Hide game modes
        if self.game_instance:
            # Ensure that the game_instance has a reference to the main menu
            if hasattr(self.game_instance, 'main_menu'):
                self.game_instance.main_menu.main_menu()  # Call the main_menu method on the MainMenu instance

    def update(self, event):
        if self.visible:
            for button in self.buttons.values():
                button.update(event)
            self.back_button.update(event)
        else:
            # Disable buttons when not visible
            for button in self.buttons.values():
                button.active = False

    def draw(self):
        if self.visible:
            for button in self.buttons.values():
                button.draw(self.screen)
            self.back_button.draw()

    def show(self):
        """Show the game mode selection."""
        self.visible = True
        for button in self.buttons.values():
            button.active = True

    def hide(self):
        """Hide the game mode selection."""
        self.visible = False
        for button in self.buttons.values():
            button.active = False