import pygame
import os
import time
from button import Button

class HeroSelection:
    def __init__(self, game_instance):
        """Initialize Hero Selection screen with character choices."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.visible = False  # Hero selection starts hidden

        # Load background border
        self.border_img = pygame.image.load(
            os.path.join(game_instance.script_dir, "images", "buttons", "game modes", "hero selection", "choose_hero_border.png")
        )

        # Character button positions
        self.positions = {
            "boy": (640, 600),  # Adjust X/Y as needed
            "girl": (1280, 600)
        }

        # Load character buttons
        self.buttons = {
            "boy": self.create_button("boy", self.positions["boy"]),
            "girl": self.create_button("girl", self.positions["girl"])
        }

        self.selected_hero = None  # Stores selected hero
        self.selection_time = None  # Stores time when selection is made

    def create_button(self, name, position):
        """Helper to create buttons for selecting a hero."""
        base_path = os.path.join(
            self.game_instance.script_dir, "images", "buttons", "game modes", "hero selection"
        )

        return Button(
            position[0], position[1],
            os.path.join(base_path, f"{name}_hero_border_img.png"),
            os.path.join(base_path, f"{name}_hero_border_hover.png"),
            os.path.join(base_path, f"{name}_hero_border_click.png"),
            lambda: self.select_hero(name),
            scale=1.0,
            audio_manager=self.game_instance.audio_manager
        )

    def select_hero(self, hero):
        """Handles character selection and freezes input for 2 seconds."""
        if self.selection_time is None:  # Prevent multiple clicks
            print(f"Hero {hero.upper()} selected!")
            self.selected_hero = hero
            self.selection_time = time.time()  # Start 2-second delay

    def update(self, event):
        """Handles button interactions and enforces click delay."""
        if self.visible:
            if self.selection_time is None:  # No freeze, allow input
                for button in self.buttons.values():
                    button.update(event)
            else:
                # Check if 2 seconds have passed since selection
                if time.time() - self.selection_time > 2:
                    print(f"Confirmed {self.selected_hero.upper()} as the hero!")
                    self.selection_time = None  # Reset delay
                    self.visible = False  # Hide selection screen
                    # TODO: Move to the next game phase

    def draw(self):
        """Draw background and the active screen."""
        self.screen.fill((0, 0, 0))  # Clear screen

        if self.visible:
            print("Drawing Hero Selection Screen!")  # ✅ Debugging
            # Draw the background border
            self.screen.blit(self.border_img, (0, 0))
            # Draw the character buttons
            for button in self.buttons.values():
                button.draw(self.screen)
        else:
            # If not visible, draw the main menu
            self.game_instance.main_menu.draw()

        pygame.display.update()

    def show(self):
        """Show the hero selection screen."""
        self.visible = True
        self.selected_hero = None
        self.selection_time = None  # Reset delay
        print("Hero selection screen opened.")

    def hide(self):
        """Hide the hero selection screen."""
        self.visible = False
        print("Hero selection screen closed.")