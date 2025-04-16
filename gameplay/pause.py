import pygame
import os
import time
from ui.button import Button
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH


class Pause:
    def __init__(self, screen, script_dir, audio_manager=None, scale=1, map_callback=None, menu_callback=None):
        self.screen = screen
        self.script_dir = script_dir
        self.audio_manager = audio_manager
        self.paused = False
        self.scale = scale
        self.pause_start_time = 0
        self.total_paused_time = 0
        self.show_confirmation = False
        self.confirmation_type = None  # 'menu' or 'map'
        self.confirmation_buttons = []

        # Callbacks for menu and map actions
        self.map_callback = map_callback
        self.menu_callback = menu_callback

        # Load fonts
        self.font = pygame.font.Font(FONT_PATH, 50)

        # Load pause button images
        pause_idle_path = os.path.join(script_dir, "assets", "images", "battle", "pause", "pause", "pause_icon_img.png")
        pause_hover_path = os.path.join(script_dir, "assets", "images", "battle", "pause", "pause", "pause_icon_hover.png")
        self.pause_idle = self.load_scaled_image(pause_idle_path)
        self.pause_hover = self.load_scaled_image(pause_hover_path)

        # Load pause border image
        border_path = os.path.join(script_dir, "assets", "images", "battle", "pause", "pause_border.png")
        self.border_img = self.load_scaled_image(border_path, 0.5)

        # Load confirmation border image
        confirm_border_path = os.path.join(script_dir, "assets", "images", "battle", "pause", "confirmation", "yesorno_border.png")
        self.confirm_border_img = self.load_scaled_image(confirm_border_path, 0.65)

        # Create pause button
        self.pause_button = Button(
            x=100,
            y=100,
            idle_img=self.pause_idle,
            hover_img=self.pause_hover,
            action=self.toggle_pause,
            scale=0.15,
            audio_manager=self.audio_manager
        )

        # Initialize pause menu icons only
        self.pause_icons = []
        self.init_pause_icons()

    def init_pause_icons(self):
        """Initialize the pause menu icons"""
        icons = [
            {
                "name": "menu",
                "pos": (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 40),
                "action": self.show_menu_confirmation
            },
            {
                "name": "map",
                "pos": (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15),
                "action": self.show_map_confirmation
            },
            {
                "name": "resume",
                "pos": (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT // 2 + 40),
                "action": self.toggle_pause
            },
        ]

        for icon in icons:
            # Load icon images
            idle_img = self.load_scaled_image(
                os.path.join(self.script_dir, "assets", "images", "battle", "pause", icon["name"],
                             f"{icon['name']}_icon_img.png"),
                0.25
            )
            hover_img = self.load_scaled_image(
                os.path.join(self.script_dir, "assets", "images", "battle", "pause", icon["name"],
                             f"{icon['name']}_icon_hover.png"),
                0.25
            )

            # Create icon
            button = Button(
                x=icon["pos"][0],
                y=icon["pos"][1],
                idle_img=idle_img,
                hover_img=hover_img,
                action=icon["action"],
                scale=1,
                audio_manager=self.audio_manager
            )

            self.pause_icons.append(button)

    def init_confirmation_buttons(self):
        """Initialize confirmation dialog buttons"""
        self.confirmation_buttons = []

        # Load button images
        yes_idle = self.load_scaled_image(
            os.path.join(self.script_dir, "assets", "images", "battle", "pause", "confirmation", "yes_btn_img.png"),
            0.4
        )
        yes_hover = self.load_scaled_image(
            os.path.join(self.script_dir, "assets", "images", "battle", "pause", "confirmation", "yes_btn_hover.png"),
            0.4
        )

        no_idle = self.load_scaled_image(
            os.path.join(self.script_dir, "assets", "images", "battle", "pause", "confirmation", "no_btn_img.png"),
            0.4
        )
        no_hover = self.load_scaled_image(
            os.path.join(self.script_dir, "assets", "images", "battle", "pause", "confirmation", "no_btn_hover.png"),
            0.4
        )

        # Create buttons
        yes_button = Button(
            x=SCREEN_WIDTH // 2 - 250,
            y=SCREEN_HEIGHT // 2 + 150,
            idle_img=yes_idle,
            hover_img=yes_hover,
            action=self.confirm_action,
            scale=1,
            audio_manager=self.audio_manager
        )

        no_button = Button(
            x=SCREEN_WIDTH // 2 + 250,
            y=SCREEN_HEIGHT // 2 + 150,
            idle_img=no_idle,
            hover_img=no_hover,
            action=self.cancel_confirmation,
            scale=1,
            audio_manager=self.audio_manager
        )

        self.confirmation_buttons.extend([yes_button, no_button])

    def show_menu_confirmation(self):
        """Show confirmation dialog for returning to menu"""
        self.show_confirmation = True
        self.confirmation_type = 'menu'
        self.init_confirmation_buttons()

    def show_map_confirmation(self):
        """Show confirmation dialog for opening map"""
        self.show_confirmation = True
        self.confirmation_type = 'map'
        self.init_confirmation_buttons()

    def confirm_action(self):
        """Handle confirmation (Yes button click)"""
        print(f"Yes clicked for {self.confirmation_type}")

        if self.confirmation_type == 'menu':
            # Use menu callback if provided
            print(f"Yes clicked for {self.confirmation_type}")
            if self.menu_callback:
                print("Calling menu callback")
                self.menu_callback()  # Ensure this function is correctly defined
                self.paused = False  # Unpause the game before returning to menu
            else:
                print("No menu callback provided.")
        elif self.confirmation_type == 'map':
            # Use map callback if provided
            if self.map_callback:
                print("Calling map callback")
                self.map_callback()
            else:
                print("No map callback provided.")

        # Cancel confirmation dialog
        self.cancel_confirmation()

    def cancel_confirmation(self):
        """Cancel confirmation dialog (No button click)"""
        self.show_confirmation = False
        self.confirmation_type = None
        self.confirmation_buttons = []

    def load_scaled_image(self, path, scale=None):
        """Load an image and scale it. If scale is None, use self.scale"""
        image = pygame.image.load(path).convert_alpha()
        scale_factor = scale if scale is not None else self.scale
        if scale_factor != 1.0:
            new_width = int(image.get_width() * scale_factor)
            new_height = int(image.get_height() * scale_factor)
            return pygame.transform.scale(image, (new_width, new_height))
        return image

    def toggle_pause(self):
        """Toggle pause state and play click sound"""
        self.paused = not self.paused
        if self.audio_manager:
            self.audio_manager.play_sfx()

            if self.paused:
                self.pause_start_time = time.time()
                pygame.mixer.music.pause()
            else:
                self.total_paused_time += time.time() - self.pause_start_time
                pygame.mixer.music.unpause()

    def return_to_menu(self):
        """Return to main menu function"""
        print("Returning to menu...")
        if self.audio_manager:
            self.audio_manager.play_sfx()

    def open_map(self):
        """Open map function"""
        print("Opening map...")
        if self.audio_manager:
            self.audio_manager.play_sfx()

    def get_total_paused_time(self):
        """Returns the total time spent paused and resets the counter"""
        paused_time = self.total_paused_time
        self.total_paused_time = 0
        return paused_time

    def draw_pause_overlay(self):
        """Draw the pause overlay when game is paused"""
        if self.paused:
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            if not self.show_confirmation:
                # Draw normal pause menu
                border_rect = self.border_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(self.border_img, border_rect)

                # Draw pause icons
                for icon in self.pause_icons:
                    icon.draw(self.screen)
            else:
                # Draw confirmation dialog
                confirm_rect = self.confirm_border_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(self.confirm_border_img, confirm_rect)

                # Draw confirmation buttons
                for button in self.confirmation_buttons:
                    button.draw(self.screen)

    def draw(self):
        """Draw the pause button (always visible) and overlay when paused"""
        if not self.paused:
            self.pause_button.draw(self.screen)
        self.draw_pause_overlay()

    def update(self, event):
        """Handle pause button events"""
        if not self.paused:
            self.pause_button.update(event)
        else:
            if self.show_confirmation:
                # Handle confirmation dialog events
                for button in self.confirmation_buttons:
                    button.update(event)
            else:
                # Handle pause menu events
                for icon in self.pause_icons:
                    icon.update(event)

    def is_paused(self):
        """Check if game is paused"""
        return self.paused