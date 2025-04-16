import pygame
import os

class Exit:
    def __init__(self, screen, script_dir, exit_callback=None, audio_manager=None):
        self.screen = screen
        self.script_dir = script_dir
        self.exit_callback = exit_callback
        self.audio_manager = audio_manager

        # Exit state
        self.show_exit_confirmation = False

        # Load exit assets
        self.load_exit_assets()
        self.create_exit_buttons()

    def load_exit_assets(self):
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT

        # Load exit confirmation assets
        quit_border_img = os.path.join(self.script_dir, "assets", "images", "buttons", "exit", "exit_border.png")
        self.exit_border = pygame.image.load(quit_border_img)
        self.exit_border = pygame.transform.scale(self.exit_border, (700, 400))
        self.exit_border_rect = self.exit_border.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Load exit button images
        self.exit_button_images = {
            'yes': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "exit", "yes_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "exit", "yes_btn_hover.png")
            },
            'no': {
                'normal': os.path.join(self.script_dir, "assets", "images", "buttons", "exit", "no_btn_img.png"),
                'hover': os.path.join(self.script_dir, "assets", "images", "buttons", "exit", "no_btn_hover.png")
            }
        }

    def create_exit_buttons(self):
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        from .button import Button

        # Yes button
        self.yes_button = Button(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 130,
                                 self.exit_button_images['yes']['normal'],
                                 self.exit_button_images['yes']['hover'],
                                 None, self.confirm_exit, scale=0.4, audio_manager=self.audio_manager)

        # No button
        self.no_button = Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT // 2 + 130,
                                self.exit_button_images['no']['normal'],
                                self.exit_button_images['no']['hover'],
                                None, self.cancel_exit, scale=0.4, audio_manager=self.audio_manager)

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

    def handle_events(self, event):
        if self.show_exit_confirmation:
            self.yes_button.update(event)
            self.no_button.update(event)

    def draw(self):
        if self.show_exit_confirmation:
            # Draw exit confirmation dialog
            self.screen.blit(self.exit_border, self.exit_border_rect.topleft)
            self.yes_button.draw(self.screen)
            self.no_button.draw(self.screen)