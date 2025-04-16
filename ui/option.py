import pygame
import os

class Options:
    def __init__(self, screen, audio_manager, script_dir):
        self.screen = screen
        self.audio_manager = audio_manager
        self.script_dir = script_dir

        # Settings state
        self.show_settings = False
        self.show_apply_changes = False
        self.audio_enabled = True
        self.temp_audio_enabled = True
        self.menu_buttons = []  # Store menu buttons

        # Load settings assets
        self.load_settings_assets()
        self.create_settings_buttons()

    def load_settings_assets(self):
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT

        # Load settings border
        settings_border_img = os.path.join(self.script_dir, "assets", "images", "buttons", "settings",
                                           "settings_border.png")
        self.settings_border = pygame.image.load(settings_border_img)
        self.settings_border = pygame.transform.scale(self.settings_border, (700, 400))
        self.settings_border_rect = self.settings_border.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Load apply changes border
        apply_changes_border_img = os.path.join(self.script_dir, "assets", "images", "buttons", "settings",
                                                "apply_changes_border.png")
        self.apply_changes_border = pygame.image.load(apply_changes_border_img)
        self.apply_changes_border = pygame.transform.scale(self.apply_changes_border, (700, 400))
        self.apply_changes_border_rect = self.apply_changes_border.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Load audio toggle images
        self.audio_on_img = pygame.image.load(
            os.path.join(self.script_dir, "assets", "images", "buttons", "settings", "music_on.png"))
        self.audio_off_img = pygame.image.load(
            os.path.join(self.script_dir, "assets", "images", "buttons", "settings", "music_off.png"))
        self.audio_on_img = pygame.transform.scale(self.audio_on_img, (150, 130))
        self.audio_off_img = pygame.transform.scale(self.audio_off_img, (150, 130))

        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.audio_img_rect = self.audio_on_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))

        # Load apply/discard button images
        self.settings_button_images = {
            'apply': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "settings", "apply_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "settings", "apply_btn_hover.png")
            },
            'discard': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "settings",
                                       "discard_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "settings",
                                      "discard_btn_hover.png")
            }
        }

    def create_settings_buttons(self):
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        from .button import Button

        # Initialize buttons with image paths and actions
        self.audio_toggle_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10,
                                          self.audio_on_img, self.audio_on_img,
                                          None, self.toggle_audio,
                                          scale=1.0, audio_manager=self.audio_manager
                                          )

        # Apply button
        self.apply_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 130,
                                   self.settings_button_images['apply']['normal'],
                                   self.settings_button_images['apply']['hover'],
                                   None, self.apply_settings, scale=0.4, audio_manager=self.audio_manager)

        # Discard button
        self.discard_button = Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 + 130,
                                     self.settings_button_images['discard']['normal'],
                                     self.settings_button_images['discard']['hover'],
                                     None, self.discard_settings, scale=0.4, audio_manager=self.audio_manager)

        # Confirm apply button
        self.confirm_apply_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 130,
                                           self.settings_button_images['apply']['normal'],
                                           self.settings_button_images['apply']['hover'],
                                           None, self.confirm_apply_settings, scale=0.4,
                                           audio_manager=self.audio_manager)

        # Cancel apply button
        self.cancel_apply_button = Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 + 130,
                                          self.settings_button_images['discard']['normal'],
                                          self.settings_button_images['discard']['hover'],
                                          None, self.cancel_apply_settings, scale=0.4, audio_manager=self.audio_manager)

    def open_options(self, menu_buttons):
        print("Options button clicked!")
        self.show_settings = True
        # Store menu buttons for later use
        self.menu_buttons = menu_buttons
        # Save current settings for potential discard
        self.temp_audio_enabled = self.audio_enabled
        # Disable main menu buttons when settings are open
        for button in menu_buttons:
            button.active = False

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
        # Use stored menu buttons from open_options
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

    def handle_events(self, event, menu_buttons=None):
        # Store menu buttons if provided
        if menu_buttons:
            self.menu_buttons = menu_buttons

        if self.show_settings:
            if self.show_apply_changes:
                self.confirm_apply_button.update(event)
                self.cancel_apply_button.update(event)
            else:
                self.audio_toggle_button.update(event)
                self.apply_button.update(event)
                self.discard_button.update(event)

    def draw(self):
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT

        if self.show_settings:
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