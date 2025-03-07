import pygame
import os
import time
from button import Button
from back_button import BackButton
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class HeroSelection:
    def __init__(self, game_instance, background_menu):
        """Initialize Hero Selection screen with character choices."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.visible = False  # Hero selection starts hidden
        self.background_menu = background_menu  # Use the same video background as MainMenu and GameModes

        # Load background border with scaling
        border_path = os.path.join(game_instance.script_dir, "images", "buttons", "game modes", "hero selection",
                                   "choose_hero_border.png")
        self.border_img = pygame.image.load(border_path)
        self.border_scale = 1.0  # Default scale for the border
        self.border_img = pygame.transform.scale(self.border_img, (
            int(self.border_img.get_width() * self.border_scale),
            int(self.border_img.get_height() * self.border_scale)
        ))
        self.border_rect = self.border_img.get_rect(center=(SCREEN_WIDTH // 2 , SCREEN_HEIGHT // 2))

        # Character button positions DIRECTLY on the border (overlapping it)
        self.positions = {
            "boy": (self.border_rect.centerx - 300, self.border_rect.centery + 30),  # On the left side of the border
            "girl": (self.border_rect.centerx + 300, self.border_rect.centery + 30)  # On the right side of the border
        }

        # Load character buttons with scaling (increased scale for better visibility)
        self.buttons = {
            "boy": self.create_button("boy", self.positions["boy"], scale=0.7),
            "girl": self.create_button("girl", self.positions["girl"], scale=0.7)
        }

        # Add Back button in the top-left corner
        self.back_button = BackButton(
            self.screen,
            self.game_instance.script_dir,
            self.go_back,
            audio_manager=self.game_instance.audio_manager,
            position=(100, 100),  # Top-left corner
            scale=0.25
        )

        self.selected_hero = None  # Stores selected hero
        self.selection_time = None  # Stores time when selection is made

    def create_button(self, name, position, scale=1.0):
        """Helper to create buttons for selecting a hero."""
        base_path = os.path.join(
            self.game_instance.script_dir, "images", "buttons", "game modes", "hero selection"
        )
        print(f"Creating {name} button at {position} with scale {scale}")  # Debug button creation
        return Button(
            position[0], position[1],
            os.path.join(base_path, f"{name}_hero_border_img.png"),
            os.path.join(base_path, f"{name}_hero_border_hover.png"),
            os.path.join(base_path, f"{name}_hero_border_click.png"),
            lambda: self.select_hero(name),
            scale=scale,
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
                self.back_button.update(event)
            else:
                # Check if 2 seconds have passed since selection
                if time.time() - self.selection_time > 2:
                    print(f"Confirmed {self.selected_hero.upper()} as the hero!")
                    self.selection_time = None  # Reset delay
                    self.visible = False  # Hide selection screen
                    # TODO: Move to the next game phase

    def draw(self):
        """Draw background and the active screen."""
        # Draw the video background
        frame_surface = self.background_menu.get_frame()
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(frame_surface, (0, 0))

        if self.visible:
            # Draw the background border first
            self.screen.blit(self.border_img, self.border_rect.topleft)

            # Ensure character selection buttons are drawn on top of the border
            for name, button in self.buttons.items():
                button.draw(self.screen)  # Buttons will now be in front

            # Draw the back button on top of everything else
            self.back_button.draw()

        pygame.display.update()

    def show(self):
        """Show the hero selection screen."""
        self.visible = True
        self.selected_hero = None
        self.selection_time = None  # Reset delay
        for button in self.buttons.values():
            button.visible = True
            button.active = True
        print("Hero selection screen opened.")

    def hide(self):
        """Hide the hero selection screen."""
        self.visible = False
        print("Hero selection screen closed.")

    def go_back(self):
        """Handles Back button click."""
        print("Back button clicked!")
        self.hide()  # Hide hero selection
        if self.game_instance:
            self.game_instance.game_modes.show()  # Show game modes
