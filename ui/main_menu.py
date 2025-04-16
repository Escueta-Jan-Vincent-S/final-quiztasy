import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from .button import Button
from managers.audio_manager import AudioManager
from .game_modes import GameModes
from .back_button import BackButton
from .hero_selection import HeroSelection
from .option import Options  # Import the new Options class
from .exit import Exit  # Import the new Exit class

class MainMenu:
    def __init__(self, screen, audio_manager, script_dir, exit_callback=None, game_instance=None):
        self.screen = screen
        self.audio_manager = audio_manager
        self.script_dir = script_dir
        self.exit_callback = exit_callback
        self.game_instance = game_instance
        self.visible = True
        self.show_game_logo = True

        # Load assets
        self.load_assets()
        self.create_buttons()

        # Initialize separate options and exit handlers
        self.options_handler = Options(screen, audio_manager, script_dir)
        self.exit_handler = Exit(screen, script_dir, exit_callback, audio_manager)

        # Only create GameModes if game_instance is None
        if not self.game_instance:
            self.game_modes = GameModes(self.screen, self.audio_manager, self.script_dir, scale=1.0, game_instance=self)

    def load_assets(self):
        # Load game logo
        game_logo_img = os.path.join(self.script_dir, "assets", "images", "logo", "logo.png")
        self.game_logo = pygame.image.load(game_logo_img)
        self.game_logo = pygame.transform.scale(self.game_logo, (
        int(self.game_logo.get_width() * 0.75), int(self.game_logo.get_height() * 0.75)))
        custom_x = 1070
        custom_y = 220
        self.game_logo_rect = self.game_logo.get_rect(centerx=custom_x, centery=custom_y)

        # Load menu button images
        self.button_images = {
            'play': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "play_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "play_btn_hover.png"),
                'click': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "play_btn_click.png")
            },
            'options': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "options_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "options_btn_hover.png"),
                'click': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "options_btn_click.png")
            },
            'credits': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "credits_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "credits_btn_hover.png"),
                'click': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "credits_btn_click.png")
            },
            'exit': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "quit_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "quit_btn_hover.png"),
                'click': os.path.join(self.script_dir, "assets", "images", "buttons", "menu", "quit_btn_click.png")
            }
        }

    def create_buttons(self):
        # Create main menu buttons
        self.play_button = Button(920, 670, self.button_images['play']['normal'],
          self.button_images['play']['hover'],
          self.button_images['play']['click'],
          self.play_game, scale=0.50, audio_manager=self.audio_manager)

        self.options_button = Button(920, 750, self.button_images['options']['normal'],
         self.button_images['options']['hover'],
         self.button_images['options']['click'],
         self.open_options, scale=0.50, audio_manager=self.audio_manager)

        self.credits_button = Button(920, 830, self.button_images['credits']['normal'],
         self.button_images['credits']['hover'],
         self.button_images['credits']['click'],
         self.show_credits, scale=0.50, audio_manager=self.audio_manager)

        self.exit_button = Button(920, 910, self.button_images['exit']['normal'],
          self.button_images['exit']['hover'],
          self.button_images['exit']['click'],
          self.exit_game, scale=0.50, audio_manager=self.audio_manager)

        self.menu_buttons = [self.play_button, self.options_button, self.credits_button, self.exit_button]

    def play_game(self):
        print("Play button clicked!")
        self.main_menu()  # Hide main menu
        self.show_game_logo = False  # Hide the game logo
        # Use game_instance.game_modes if available, otherwise use self.game_modes
        if self.game_instance:
            self.game_instance.game_modes.show()
        else:
            self.game_modes.show()
        # Hide main menu buttons
        for button in self.menu_buttons:
            button.visible = False

    def open_options(self):
        # Use the new options handler
        self.options_handler.open_options(self.menu_buttons)

    def show_credits(self):
        print("Credits button clicked!")
        # Add your credits screen logic here

    def exit_game(self):
        # Use the new exit handler
        self.exit_handler.exit_game()

    def handle_events(self, event):
        if self.exit_handler.show_exit_confirmation:
            self.exit_handler.handle_events(event)
        elif self.options_handler.show_settings:
            self.options_handler.handle_events(event, self.menu_buttons)
        else:
            # Only update main menu buttons if settings and exit confirmation are not open
            for button in self.menu_buttons:
                button.update(event)

        # For Game Modes
        if self.game_instance and self.game_instance.game_modes.visible:
            self.game_instance.game_modes.update(event)
        elif hasattr(self, 'game_modes') and self.game_modes.visible:
            self.game_modes.update(event)

    def draw(self):
        # Draw the game logo if it's visible
        if self.show_game_logo and not self.exit_handler.show_exit_confirmation and not self.options_handler.show_settings and not self.is_game_modes_visible():
            self.screen.blit(self.game_logo, self.game_logo_rect.topleft)

        # Draw based on current state
        if self.exit_handler.show_exit_confirmation:
            self.exit_handler.draw()
        elif self.options_handler.show_settings:
            self.options_handler.draw()
        else:
            # Draw main menu buttons only if GameModes is not visible
            if not self.is_game_modes_visible():
                for button in self.menu_buttons:
                    button.draw(self.screen)

        # Draw game modes if visible
        if self.game_instance and hasattr(self.game_instance, 'game_modes') and self.game_instance.game_modes.visible:
            self.game_instance.game_modes.draw()
        elif hasattr(self, 'game_modes') and self.game_modes.visible:
            self.game_modes.draw()

    def is_game_modes_visible(self):
        """Helper method to check if game modes is visible regardless of where it's stored"""
        if self.game_instance and hasattr(self.game_instance, 'game_modes'):
            return self.game_instance.game_modes.visible
        elif hasattr(self, 'game_modes'):
            return self.game_modes.visible
        return False

    def show(self):
        """Make the main menu visible."""
        self.visible = True

    def hide(self):
        """Hide the main menu."""
        self.visible = False

    def main_menu(self):
        # Ensure all main menu buttons are visible
        for button in self.menu_buttons:
            button.visible = True  # Show main menu buttons

        # Ensure the game logo is visible
        self.show_game_logo = True  # Show the game logo

        # Hide game modes based on where it exists
        if self.game_instance and hasattr(self.game_instance, 'game_modes'):
            self.game_instance.game_modes.hide()
        elif hasattr(self, 'game_modes'):
            self.game_modes.hide()