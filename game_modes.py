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
        self.show_new_continue = False  # Controls New/Continue selection

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

        # New/Continue selection screen assets
        self.new_continue_border = pygame.image.load(
            os.path.join(script_dir, "images", "buttons", "game modes", "new or continue", "border.png"))
        self.new_continue_border_rect = self.new_continue_border.get_rect(center=(960, 540))

        self.new_button = self.create_button(script_dir, "new", (960, 440), action=self.start_new_game)
        self.continue_button = self.create_button(script_dir, "continue", (960, 640), action=self.continue_game)

        # Add Back button
        self.back_button = BackButton(self.screen, script_dir, self.go_back, audio_manager=self.audio_manager,
                                      position=(100, 100), scale=0.25)

    def play_single_player(self):
        print("Playing single-player mode")
        self.show_new_continue = True  # Show new/continue prompt
        # Instead of just disabling, we'll also prevent hover effects
        for button in self.buttons.values():
            button.active = False  # Disable background buttons when prompt is active

    def start_new_game(self):
        print("Starting a new game...")
        self.show_new_continue = False
        for button in self.buttons.values():
            button.active = True  # Re-enable buttons when leaving prompt
        if self.game_instance:
            if hasattr(self.game_instance, 'hero_selection'):
                self.game_instance.hero_selection.show()
            elif hasattr(self.game_instance, 'game_instance') and hasattr(self.game_instance.game_instance,
                                                                          'hero_selection'):
                self.game_instance.game_instance.hero_selection.show()

    def continue_game(self):
        print("Continuing previous game...")
        self.show_new_continue = False
        for button in self.buttons.values():
            button.active = True  # Re-enable buttons when leaving prompt
        # TODO: Implement loading of saved progress

    def create_button(self, script_dir, name, position, action=None):
        """Helper method to create buttons with scaling."""
        folder = "new or continue" if name in ["new", "continue"] else "modes"
        img_path = os.path.join(script_dir, "images", "buttons", "game modes", folder, f"{name}_btn_img.png")
        hover_path = os.path.join(script_dir, "images", "buttons", "game modes", folder, f"{name}_btn_hover.png")
        click_path = None if folder == "modes" else os.path.join(script_dir, "images", "buttons", "game modes", folder,
                                                                 f"{name}_btn_click.png")

        return Button(
            position[0], position[1], img_path, hover_path, click_path,
            action if action else lambda: self.on_click(name), scale=self.scale, audio_manager=self.audio_manager
        )

    def on_click(self, name):
        """Handles button clicks for game mode selection."""
        print(f"Button {name} clicked!")
        if name == "sp":
            self.play_single_player()

    def go_back(self):
        """Handles Back button click."""
        print("Back button clicked!")
        if self.show_new_continue:
            self.show_new_continue = False  # Hide only the New/Continue selection
            for button in self.buttons.values():
                button.active = True  # Re-enable buttons when closing prompt
        else:
            self.hide()  # Hide game modes and return to main menu
            if self.game_instance:
                if hasattr(self.game_instance, 'main_menu'):
                    self.game_instance.main_menu.main_menu()

    def update(self, event):
        if self.visible:
            # Only update back button and active prompt buttons when new/continue is shown
            if self.show_new_continue:
                self.new_button.update(event)
                self.continue_button.update(event)
                self.back_button.update(event)
            else:
                # Update all buttons when not showing new/continue
                for button in self.buttons.values():
                    button.update(event)
                self.back_button.update(event)

    def draw(self):
        if self.visible:
            # Always draw the game mode buttons in the background
            # But don't update their hover state when prompt is active
            for button in self.buttons.values():
                button.draw(self.screen)

            # Draw the new/continue prompt on top if active
            if self.show_new_continue:
                self.screen.blit(self.new_continue_border, self.new_continue_border_rect.topleft)
                self.new_button.draw(self.screen)
                self.continue_button.draw(self.screen)

            # Always draw the back button on top
            self.back_button.draw()

    def show(self):
        """Show the game mode selection."""
        self.visible = True
        self.show_new_continue = False  # Reset this when showing the menu
        for button in self.buttons.values():
            button.active = True

    def hide(self):
        """Hide the game mode selection."""
        self.visible = False
        self.show_new_continue = False  # Reset this when hiding the menu
        for button in self.buttons.values():
            button.active = False