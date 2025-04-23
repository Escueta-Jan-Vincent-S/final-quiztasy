import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE
from ui.button import Button

class LogoutScreen:
    def __init__(self, screen, script_dir, auth_manager, audio_manager=None, on_close_callback=None):
        self.screen = screen
        self.script_dir = script_dir
        self.auth_manager = auth_manager
        self.audio_manager = audio_manager
        self.on_close_callback = on_close_callback
        self.visible = False

        # Load assets
        self.load_assets()

        # Create buttons for logout screen
        self.logout_button = Button(
            SCREEN_WIDTH // 2 - 200,
            SCREEN_HEIGHT // 2 + 275,
            idle_img=self.button_images['logout']['normal'],
            hover_img=self.button_images['logout']['hover'],
            action=self.logout,
            scale=0.5,
            audio_manager=self.audio_manager
        )

        self.cancel_button = Button(
            SCREEN_WIDTH // 2 + 225,
            SCREEN_HEIGHT // 2 + 275,
            idle_img=self.button_images['cancel']['normal'],
            hover_img=self.button_images['cancel']['hover'],
            action=self.close,
            scale=0.5,
            audio_manager=self.audio_manager
        )

        # Status message
        self.status_message = ""
        self.status_color = pygame.Color('white')
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE // 2)

        # User info
        self.user_email = ""

    def load_assets(self):
        # Load panel background
        panel_img_path = os.path.join(self.script_dir, "assets", "images", "login&register", "logout_border.png")
        if os.path.exists(panel_img_path):
            self.panel_background = pygame.image.load(panel_img_path).convert_alpha()
            scale = 0.5

            if scale != 1.0:
                original_width = self.panel_background.get_width()
                original_height = self.panel_background.get_height()
                new_size = (int(original_width * scale), int(original_height * scale))
                self.panel_background = pygame.transform.scale(self.panel_background, new_size)

        # Load button images
        img_dir = os.path.join(self.script_dir, "assets", "images", "login&register")
        self.button_images = {
            'logout': {
                'normal': os.path.join(img_dir, "logout_btn_img.png"),
                'hover': os.path.join(img_dir, "logout_btn_hover.png"),
            },
            'cancel': {
                'normal': os.path.join(img_dir, "cancel_btn_img.png"),
                'hover': os.path.join(img_dir, "cancel_btn_hover.png"),
            }
        }

    def logout(self):
        success = self.auth_manager.logout()
        if success:
            self.status_message = "Logout successful!"
            self.status_color = pygame.Color('green')
            pygame.time.set_timer(pygame.USEREVENT + 2, 1500)  # Close after 1.5 seconds
        else:
            self.status_message = "Logout Failed"
            self.status_color = pygame.Color('red')

    def close(self):
        self.visible = False
        self.status_message = ""

        # Call the callback if provided
        if self.on_close_callback:
            self.on_close_callback()

    def show(self):
        self.visible = True
        # Get current user's email to display
        current_user = self.auth_manager.get_current_user()
        if current_user:
            self.user_email = current_user["email"]
        else:
            self.user_email = ""

    def handle_events(self, event):
        if not self.visible:
            return

        if event.type == pygame.USEREVENT + 2:
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # Stop the timer
            self.close()
            return

        # Handle buttons
        self.logout_button.update(event)
        self.cancel_button.update(event)

    def update(self):
        if not self.visible:
            return

    def draw(self):
        if not self.visible:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_rect = self.panel_background.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(self.panel_background, panel_rect)

        # Draw the buttons
        self.logout_button.draw(self.screen)
        self.cancel_button.draw(self.screen)

        # Draw status message if any
        if self.status_message:
            status_surf = self.font.render(self.status_message, True, self.status_color)
            self.screen.blit(status_surf, (SCREEN_WIDTH // 2 - status_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 475))