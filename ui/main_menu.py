import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE
from .button import Button
from managers.audio_manager import AudioManager
from managers.auth_manager import AuthManager
from .game_modes import GameModes
from .back_button import BackButton
from .hero_selection import HeroSelection
from .option import Options
from .exit import Exit
from auth.login_screen import LoginScreen
from auth.logout_screen import LogoutScreen

class MainMenu:
    def __init__(self, screen, audio_manager, script_dir, exit_callback=None, game_instance=None):
        self.screen = screen
        self.audio_manager = audio_manager
        self.script_dir = script_dir
        self.exit_callback = exit_callback
        self.game_instance = game_instance
        self.visible = True
        self.show_game_logo = True

        # Initialize auth manager
        self.auth_manager = AuthManager()

        # Load assets
        self.load_assets()
        self.create_buttons()

        # Initialize separate options and exit handlers
        self.options_handler = Options(screen, audio_manager, script_dir)
        self.exit_handler = Exit(screen, script_dir, exit_callback, audio_manager)

        # Initialize login screen and logout
        self.login_screen = LoginScreen(screen, script_dir, self.auth_manager, audio_manager, self.on_login_close)
        self.logout_screen = LogoutScreen(screen, script_dir, self.auth_manager, audio_manager, self.on_logout_close)

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

        # Load login button images (with hover state)
        login_icon_path = os.path.join(self.script_dir, "assets", "images", "login&register", "login_icon_img.png")
        login_icon_hover_path = os.path.join(self.script_dir, "assets", "images", "login&register",
                                             "login_icon_hover.png")
        registered_icon_path = os.path.join(self.script_dir, "assets", "images", "login&register",
                                            "registered_icon_img.png")
        registered_icon_hover_path = os.path.join(self.script_dir, "assets", "images", "login&register",
                                                  "registered_icon_hover.png")

        # Load the login icon (normal state)
        if os.path.exists(login_icon_path):
            self.login_icon = pygame.image.load(login_icon_path)
            self.login_icon = pygame.transform.scale(self.login_icon, (125, 125))

        # Load the login icon hover image
        if os.path.exists(login_icon_hover_path):
            self.login_icon_hover = pygame.image.load(login_icon_hover_path)
            self.login_icon_hover = pygame.transform.scale(self.login_icon_hover, (125, 125))

        # Load the registered icon (normal state)
        if os.path.exists(registered_icon_path):
            self.registered_icon = pygame.image.load(registered_icon_path)
            self.registered_icon = pygame.transform.scale(self.registered_icon, (125, 125))

        # Load the registered icon hover image
        if os.path.exists(registered_icon_hover_path):
            self.registered_icon_hover = pygame.image.load(registered_icon_hover_path)
            self.registered_icon_hover = pygame.transform.scale(self.registered_icon_hover, (125, 125))

        # Create font for login text
        self.login_font = pygame.font.Font(FONT_PATH, FONT_SIZE // 2)

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

        # Create login button based on current login status
        # Set initial button state based on login status
        if self.auth_manager.get_current_user():
            button_img = self.registered_icon
            button_hover = self.registered_icon_hover
        else:
            button_img = self.login_icon
            button_hover = self.login_icon_hover

        self.login_button = Button(100, SCREEN_HEIGHT - 100,
                                   button_img,
                                   button_hover,
                                   button_img,  # No click image
                                   self.open_login_screen,
                                   scale=1.0,
                                   audio_manager=self.audio_manager)

        self.menu_buttons = [self.play_button, self.options_button, self.credits_button, self.exit_button,
                             self.login_button]

    def open_login_screen(self):
        """Open the login or logout screen based on login status"""
        current_user = self.auth_manager.get_current_user()
        if current_user:
            self.logout_screen.show()
        else:
            self.login_screen.show()

    def on_login_close(self):
        """Callback when login screen is closed"""
        # Debug: Print current user before update
        current_user_before = self.auth_manager.get_current_user()
        print(f"[DEBUG] on_login_close - Current user before update: {current_user_before}")

        # Update login button appearance when login screen closes
        self.update_login_button()

        # Debug: Print current user after update
        current_user_after = self.auth_manager.get_current_user()
        print(f"[DEBUG] on_login_close - Current user after update: {current_user_after}")

        # Debug: Compare before and after
        if current_user_before != current_user_after:
            print("[DEBUG] on_login_close - User status changed!")
        else:
            print("[DEBUG] on_login_close - User status unchanged")

    def on_logout_close(self):
        """Callback when logout screen is closed"""
        # Update login button appearance when logout screen closes
        self.update_login_button()

    def update_login_button(self):
        """Update login button based on user login status"""
        current_user = self.auth_manager.get_current_user()

        # Store current mouse position to check hover state
        mouse_pos = pygame.mouse.get_pos()
        was_hovering = self.login_button.rect.collidepoint(mouse_pos)

        # Re-create the login button with appropriate images
        if current_user:
            # Remove the old button from menu_buttons list
            if self.login_button in self.menu_buttons:
                self.menu_buttons.remove(self.login_button)

            # Create a new button with the registered icon
            self.login_button = Button(100, 100,
                                       self.registered_icon,
                                       self.registered_icon_hover,
                                       self.registered_icon,  # No click image
                                       self.open_login_screen,
                                       scale=1.0,
                                       audio_manager=self.audio_manager)
        else:
            # Remove the old button from menu_buttons list
            if self.login_button in self.menu_buttons:
                self.menu_buttons.remove(self.login_button)

            # Create a new button with the login icon
            self.login_button = Button(100, 100,
                                       self.login_icon,
                                       self.login_icon_hover,
                                       self.login_icon,  # No click image
                                       self.open_login_screen,
                                       scale=1.0,
                                       audio_manager=self.audio_manager)

        # Restore hover state if mouse is over button
        if was_hovering:
            self.login_button.image = self.login_button.hover_img

        # Add the new button to menu_buttons
        self.menu_buttons.append(self.login_button)

    def play_game(self):
        """Handle play button click with user status check"""
        # Debug: Check current user status
        current_user = self.auth_manager.get_current_user()
        if current_user:
            print(f"[DEBUG] play_game - User is logged in as: {current_user['email']}")
            # Debug: Get user stats if available
        else:
            print("[DEBUG] play_game - No user logged in (guest mode)")

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
        self.options_handler.open_options(self.menu_buttons)

    def show_credits(self):
        print("Credits button clicked!")
        print("Game Developer: Jan Vincent S. Escueta")
        print("Game Design: Alione F. Tongson")
        print("Professor: Shaira Mae Bughaw")

    def exit_game(self):
        self.exit_handler.exit_game()

    def handle_events(self, event):
        if self.login_screen.visible or (
                hasattr(self.login_screen, 'register_screen') and self.login_screen.register_screen.visible):
            previous_user = self.auth_manager.get_current_user()
            self.login_screen.handle_events(event)
            current_user = self.auth_manager.get_current_user()

            if (previous_user is None and current_user is not None) or \
                    (previous_user is not None and current_user is None):
                print("Login status changed - updating button")  # Debug output
                self.update_login_button()

        elif self.logout_screen.visible:
            previous_user = self.auth_manager.get_current_user()
            self.logout_screen.handle_events(event)
            current_user = self.auth_manager.get_current_user()

            if (previous_user is not None and current_user is None):
                print("User logged out - updating button")  # Debug output
                self.update_login_button()

        elif self.exit_handler.show_exit_confirmation:
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
        # Only draw UI elements if main menu is visible
        if not self.visible:
            return

        # Draw the game logo if it's visible
        if self.show_game_logo and not self.exit_handler.show_exit_confirmation and not self.options_handler.show_settings and not self.is_game_modes_visible():
            self.screen.blit(self.game_logo, self.game_logo_rect.topleft)

        any_screen_active = (self.login_screen.visible or (hasattr(self.login_screen, 'register_screen') and self.login_screen.register_screen.visible) or self.logout_screen.visible or self.exit_handler.show_exit_confirmation or self.options_handler.show_settings or self.is_game_modes_visible())
        # Draw based on current state
        if self.exit_handler.show_exit_confirmation:
            self.exit_handler.draw()
        elif self.options_handler.show_settings:
            self.options_handler.draw()
        else:
            # Draw main menu buttons only if GameModes is not visible
            if not self.is_game_modes_visible():
                # Reset login button to idle state if any screen is active
                if any_screen_active and self.login_button in self.menu_buttons:
                    self.login_button.image = self.login_button.idle_img

                for button in self.menu_buttons:
                    # Only draw button if it's visible
                    if getattr(button, 'visible', True):
                        button.draw(self.screen)

        # Draw login status text only if not in custom mode
        if not (self.is_game_modes_visible() and hasattr(self.game_instance, 'custom_mode_active') and self.game_instance.custom_mode_active):
            self.draw_login_status()

        # Draw game modes if visible
        if self.game_instance and hasattr(self.game_instance, 'game_modes') and self.game_instance.game_modes.visible:
            self.game_instance.game_modes.draw()
        elif hasattr(self, 'game_modes') and self.game_modes.visible:
            self.game_modes.draw()

        # Draw login screen if visible
        if self.login_screen.visible or (
                hasattr(self.login_screen, 'register_screen') and self.login_screen.register_screen.visible):
            self.login_screen.draw()
        elif self.logout_screen.visible:
            self.logout_screen.draw()

    def draw_login_status(self):
        """Draw login status text next to login button."""
        current_user = self.auth_manager.get_current_user()
        if not (self.options_handler.show_settings or self.exit_handler.show_exit_confirmation):
            # Update login button images based on login status
            self.update_login_button()

            if current_user:
                status_text = current_user["email"]
            else:
                status_text = "Login/Register"

            # Render and draw the text
            text_surf = self.login_font.render(status_text, True, pygame.Color('white'))
            self.screen.blit(text_surf, (175, 100))

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
        # Update login button when showing the main menu
        self.update_login_button()

    def hide(self):
        """Hide the main menu."""
        self.visible = False

    def main_menu(self):
        # Ensure all main menu buttons are visible
        for button in self.menu_buttons:
            button.visible = True  # Show main menu buttons

        # Ensure the game logo is visible
        self.show_game_logo = True  # Show the game logo

        # Update login button when returning to main menu
        self.update_login_button()

        # Hide game modes based on where it exists
        if self.game_instance and hasattr(self.game_instance, 'game_modes'):
            self.game_instance.game_modes.hide()
        elif hasattr(self, 'game_modes'):
            self.game_modes.hide()