import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from button import Button
from audio_manager import AudioManager
from game_modes import GameModes
from back_button import BackButton
from hero_selection import HeroSelection


class MainMenu:
    def __init__(self, screen, audio_manager, script_dir, exit_callback=None, game_instance=None):
        self.screen = screen
        self.audio_manager = audio_manager
        self.script_dir = script_dir
        self.show_exit_confirmation = False
        self.show_settings = False
        self.show_apply_changes = False
        self.audio_enabled = True  # Single audio control
        self.temp_audio_enabled = True  # For settings changes
        self.show_game_logo = True
        self.exit_callback = exit_callback  # Callback function to exit the game
        self.game_instance = game_instance  # Store the actual game instance
        self.visible = True

        # Load assets
        self.load_assets()
        self.create_buttons()
        # Only create GameModes if game_instance is None
        if not self.game_instance:
            self.game_modes = GameModes(self.screen, self.audio_manager, self.script_dir, scale=1.0, game_instance=self)

    def load_assets(self):
        # Load game logo
        game_logo_img = os.path.join(self.script_dir, "images", "logo", "logo.png")
        self.game_logo = pygame.image.load(game_logo_img)
        self.game_logo = pygame.transform.scale(self.game_logo, (
        int(self.game_logo.get_width() * 0.75), int(self.game_logo.get_height() * 0.75)))
        custom_x = 1070
        custom_y = 220
        self.game_logo_rect = self.game_logo.get_rect(centerx=custom_x, centery=custom_y)

        # Load menu button images
        self.button_images = {
            'play': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "menu", "play_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "menu", "play_btn_hover.png"),
                'click': os.path.join(self.script_dir, "images", "buttons", "menu", "play_btn_click.png")
            },
            'options': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "menu", "options_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "menu", "options_btn_hover.png"),
                'click': os.path.join(self.script_dir, "images", "buttons", "menu", "options_btn_click.png")
            },
            'credits': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "menu", "credits_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "menu", "credits_btn_hover.png"),
                'click': os.path.join(self.script_dir, "images", "buttons", "menu", "credits_btn_click.png")
            },
            'exit': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "menu", "quit_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "menu", "quit_btn_hover.png"),
                'click': os.path.join(self.script_dir, "images", "buttons", "menu", "quit_btn_click.png")
            }
        }

        # Load exit confirmation assets
        quit_border_img = os.path.join(self.script_dir, "images", "buttons", "exit", "exit_border.png")
        self.exit_border = pygame.image.load(quit_border_img)
        self.exit_border = pygame.transform.scale(self.exit_border, (700, 400))
        self.exit_border_rect = self.exit_border.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.exit_button_images = {
            'yes': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "exit", "yes_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "exit", "yes_btn_hover.png")
            },
            'no': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "exit", "no_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "exit", "no_btn_hover.png")
            }
        }

        # Load settings assets
        settings_border_img = os.path.join(self.script_dir, "images", "buttons", "settings", "settings_border.png")
        self.settings_border = pygame.image.load(settings_border_img)
        self.settings_border = pygame.transform.scale(self.settings_border, (700, 400))
        self.settings_border_rect = self.settings_border.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Load apply changes border
        apply_changes_border_img = os.path.join(self.script_dir, "images", "buttons", "settings",
                                                "apply_changes_border.png")
        self.apply_changes_border = pygame.image.load(apply_changes_border_img)
        self.apply_changes_border = pygame.transform.scale(self.apply_changes_border, (700, 400))
        self.apply_changes_border_rect = self.apply_changes_border.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Load audio toggle images
        self.audio_on_img = pygame.image.load(
            os.path.join(self.script_dir, "images", "buttons", "settings", "music_on.png"))
        self.audio_off_img = pygame.image.load(
            os.path.join(self.script_dir, "images", "buttons", "settings", "music_off.png"))
        self.audio_on_img = pygame.transform.scale(self.audio_on_img, (150, 130))
        self.audio_off_img = pygame.transform.scale(self.audio_off_img, (150, 130))
        self.audio_img_rect = self.audio_on_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))

        # Load apply/discard button images
        self.settings_button_images = {
            'apply': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "settings", "apply_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "settings", "apply_btn_hover.png")
            },
            'discard': {
                'normal': os.path.join(self.script_dir, "images", "buttons", "settings", "discard_btn_img.png"),
                'hover': os.path.join(self.script_dir, "images", "buttons", "settings", "discard_btn_hover.png")
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

        # Create exit confirmation buttons
        self.yes_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 130,
         self.exit_button_images['yes']['normal'],
         self.exit_button_images['yes']['hover'],
         None, self.confirm_exit, scale=0.4, audio_manager=self.audio_manager)

        self.no_button = Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 + 130,
            self.exit_button_images['no']['normal'],
            self.exit_button_images['no']['hover'],
            None, self.cancel_exit, scale=0.4, audio_manager=self.audio_manager)

        # Create settings buttons
        self.audio_toggle_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10,
            self.audio_on_img, self.audio_on_img,
            None, self.toggle_audio,
            scale=1.0, audio_manager=self.audio_manager
        )

        self.apply_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 130,
           self.settings_button_images['apply']['normal'],
           self.settings_button_images['apply']['hover'],
           None, self.apply_settings, scale=0.4, audio_manager=self.audio_manager)

        self.discard_button = Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 + 130,
         self.settings_button_images['discard']['normal'],
         self.settings_button_images['discard']['hover'],
         None, self.discard_settings, scale=0.4, audio_manager=self.audio_manager)

        self.confirm_apply_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 130,
           self.settings_button_images['apply']['normal'],
           self.settings_button_images['apply']['hover'],
           None, self.confirm_apply_settings, scale=0.4,
           audio_manager=self.audio_manager)

        self.cancel_apply_button = Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 + 130,
          self.settings_button_images['discard']['normal'],
          self.settings_button_images['discard']['hover'],
          None, self.cancel_apply_settings, scale=0.4, audio_manager=self.audio_manager)

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
        print("Options button clicked!")
        self.show_settings = True
        # Save current settings for potential discard
        self.temp_audio_enabled = self.audio_enabled
        # Disable main menu buttons when settings are open
        for button in self.menu_buttons:
            button.active = False

    def show_credits(self):
        print("Credits button clicked!")
        # Add your credits screen logic here

    def exit_game(self):
        print("Exit button clicked!")
        self.show_exit_confirmation = True

    def confirm_exit(self):
        """Handles the confirmation of exiting the game."""
        print("Exiting game...")
        if self.exit_callback:
            self.exit_callback()  # Call the exit callback function

    def cancel_exit(self):
        self.show_exit_confirmation = False

    def toggle_audio(self):
        print("Audio toggle clicked!")
        self.temp_audio_enabled = not self.temp_audio_enabled
        self.audio_manager.toggle_audio()  # Mute/unmute audio instantly

    def apply_settings(self):
        print("Apply settings clicked!")
        # Show confirmation dialog
        self.show_apply_changes = True

    def discard_settings(self):
        print("Discard settings clicked!")
        # If the setting was changed, toggle it back
        if self.temp_audio_enabled != self.audio_enabled:
            self.toggle_audio()  # Restore original audio state
        self.show_settings = False
        # Re-enable main menu buttons when settings are closed
        for button in self.menu_buttons:
            button.active = True

    def confirm_apply_settings(self):
        print("Confirming settings...")
        # Apply settings permanently
        self.audio_enabled = self.temp_audio_enabled
        self.show_apply_changes = False
        self.show_settings = False
        # Re-enable main menu buttons when settings are closed
        for button in self.menu_buttons:
            button.active = True

    def cancel_apply_settings(self):
        print("Canceling apply confirmation...")
        self.show_apply_changes = False

    def show(self):
        """Make the main menu visible."""
        self.visible = True

    def hide(self):
        """Hide the main menu."""
        self.visible = False

    def handle_events(self, event):
        if self.show_exit_confirmation:
            self.yes_button.update(event)
            self.no_button.update(event)
        elif self.show_settings:
            if self.show_apply_changes:
                self.confirm_apply_button.update(event)
                self.cancel_apply_button.update(event)
            else:
                self.audio_toggle_button.update(event)
                self.apply_button.update(event)
                self.discard_button.update(event)
        else:
            # Only update main menu buttons if settings are not open
            for button in self.menu_buttons:
                button.update(event)

        # For Game Modes
        if self.game_instance and self.game_instance.game_modes.visible:
            self.game_instance.game_modes.update(event)
        elif hasattr(self, 'game_modes') and self.game_modes.visible:
            self.game_modes.update(event)

    def is_game_modes_visible(self):
        """Helper method to check if game modes is visible regardless of where it's stored"""
        if self.game_instance and hasattr(self.game_instance, 'game_modes'):
            return self.game_instance.game_modes.visible
        elif hasattr(self, 'game_modes'):
            return self.game_modes.visible
        return False

    def draw(self):
        # Draw the game logo if it's visible
        if self.show_game_logo and not self.show_exit_confirmation and not self.show_settings and not self.is_game_modes_visible():
            self.screen.blit(self.game_logo, self.game_logo_rect.topleft)

        # Draw based on current state
        if self.show_exit_confirmation:
            # Draw exit confirmation dialog
            self.screen.blit(self.exit_border, self.exit_border_rect.topleft)
            self.yes_button.draw(self.screen)
            self.no_button.draw(self.screen)
        elif self.show_settings:
            # Draw settings dialog
            self.screen.blit(self.settings_border, self.settings_border_rect.topleft)

            # Draw the appropriate audio icon based on status
            audio_img = self.audio_on_img if self.temp_audio_enabled else self.audio_off_img
            self.screen.blit(audio_img, self.audio_img_rect.topleft)

            if self.show_apply_changes:
                # Draw apply changes confirmation
                self.screen.blit(self.apply_changes_border, self.apply_changes_border_rect.topleft)
                self.confirm_apply_button.draw(self.screen)
                self.cancel_apply_button.draw(self.screen)
            else:
                # Draw apply/discard buttons
                self.apply_button.draw(self.screen)
                self.discard_button.draw(self.screen)
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

    def main_menu(self):
        for button in self.menu_buttons:
            button.visible = True  # Show main menu buttons
        self.show_game_logo = True  # Show the game logo

        # Hide game modes based on where it exists
        if self.game_instance and hasattr(self.game_instance, 'game_modes'):
            self.game_instance.game_modes.hide()
        elif hasattr(self, 'game_modes'):
            self.game_modes.hide()