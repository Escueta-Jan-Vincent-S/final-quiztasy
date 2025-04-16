import pygame
import os
import time
import random
from .button import Button
from .back_button import BackButton
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

CONFIRMATION_DELAY = pygame.USEREVENT + 1

class HeroSelection:
    def __init__(self, game_instance, background_menu):
        """Initialize Hero Selection screen with character choices."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.visible = False  # Hero selection starts hidden
        self.background_menu = background_menu
        self.audio_manager = game_instance.audio_manager

        # Load background border
        border_path = os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "choose_hero_border.png")
        self.border_img = pygame.image.load(border_path)
        self.border_rect = self.border_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Character button positions
        self.positions = {
            "boy": (self.border_rect.centerx - 300, self.border_rect.centery + 30),
            "girl": (self.border_rect.centerx + 300, self.border_rect.centery + 30)
        }

        # Load character buttons with scaling
        self.buttons = {
            "boy": self.create_button("boy", self.positions["boy"], scale=0.7, freeze_duration=1),
            "girl": self.create_button("girl", self.positions["girl"], scale=0.7, freeze_duration=1)
        }

        # Add Back button
        self.back_button = BackButton(
            self.screen,
            self.game_instance.script_dir,
            self.go_back,
            audio_manager=self.game_instance.audio_manager,
            position=(100, 100),
            scale=0.25
        )

        # Load hero voicelines
        self.voicelines = {
            "boy": [
                os.path.join(game_instance.script_dir, "assets", "audio", "voiceline", "boy", "hero selection", f"boy_voice_{i}.mp3") for i in range(1, 4)
            ],
            "girl": [
                os.path.join(game_instance.script_dir, "assets", "audio", "voiceline", "girl", "hero selection", f"girl_voice_{i}.mp3") for i in range(1, 4)
            ]
        }

        # Confirmation dialog setup
        self.confirmation_active = False
        self.temp_selected_hero = None

        # Load confirmation border with scaling
        confirmation_border_path = os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "yes_or_no_border.png")
        self.confirmation_border_original = pygame.image.load(confirmation_border_path)

        # Apply scaling to confirmation border
        border_scale = 0.7
        border_width = int(self.confirmation_border_original.get_width() * border_scale)
        border_height = int(self.confirmation_border_original.get_height() * border_scale)
        self.confirmation_border = pygame.transform.scale(self.confirmation_border_original,(border_width, border_height))
        self.confirmation_border_rect = self.confirmation_border.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Create Yes/No buttons with appropriate scaling
        yes_btn_position = (self.confirmation_border_rect.centerx - 200, self.confirmation_border_rect.centery + 150)
        no_btn_position = (self.confirmation_border_rect.centerx + 200, self.confirmation_border_rect.centery + 150)

        button_scale = 0.6  # Scale for the yes/no buttons

        self.yes_button = Button(
            yes_btn_position[0], yes_btn_position[1],
            os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "yes_btn_img.png"),
            os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "yes_btn_hover.png"),
            action=self.confirm_hero_selection,
            scale=button_scale,
            audio_manager=self.game_instance.audio_manager
        )

        self.no_button = Button(
            no_btn_position[0], no_btn_position[1],
            os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "no_btn_img.png"),
            os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "no_btn_hover.png"),
            action=self.cancel_hero_selection,
            scale=button_scale,
            audio_manager=self.game_instance.audio_manager
        )

        self.selected_hero = None
        self.selection_time = None
        self.voiceline_sound = None

    def create_button(self, name, position, scale=1.0, freeze_duration=0):
        """Helper to create buttons with optional freeze duration."""
        base_path = os.path.join(self.game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection")
        return Button(
            position[0], position[1],
            os.path.join(base_path, f"{name}_hero_border_img.png"),
            os.path.join(base_path, f"{name}_hero_border_hover.png"),
            os.path.join(base_path, f"{name}_hero_border_click.png"),
            lambda hero=name: self.pre_select_hero(hero),  # Changed to pre_select_hero
            scale=scale,
            audio_manager=self.game_instance.audio_manager,
            freeze_duration=freeze_duration
        )

    def play_random_voiceline(self, hero):
        """Play a random voiceline for the selected hero if audio is enabled."""
        if not self.audio_manager.audio_enabled:  # 🔇 Check if audio is muted
            print(f"Audio is muted. Skipping {hero} voiceline.")
            return
        if self.voiceline_sound:
            self.voiceline_sound.stop()
        try:
            random_voiceline = random.choice(self.voicelines[hero])
            self.voiceline_sound = pygame.mixer.Sound(random_voiceline)
            self.voiceline_sound.play()
        except Exception as e:
            print(f"Error playing voiceline: {e}")

    def pre_select_hero(self, hero):
        """Initial hero selection that starts a 1-second delay before confirmation."""
        print(f"Pre-selecting hero: {hero.upper()}")

        # Play hero voiceline immediately
        self.play_random_voiceline(hero)

        # Set the button to "clicked" image
        for button_name, button in self.buttons.items():
            if button_name == hero:
                button.image = button.click_img
            else:
                button.image = button.idle_img

        # Disable hero buttons while waiting
        for button in self.buttons.values():
            button.active = False

        # Start a 1-second timer for confirmation
        self.temp_selected_hero = hero
        pygame.time.set_timer(CONFIRMATION_DELAY, 1000, loops=1)  # Trigger event after 1s

    def confirm_hero_selection(self):
        """User confirmed hero selection with 'Yes' button."""
        print(f"Hero {self.temp_selected_hero.upper()} selection confirmed!")
        self.selected_hero = self.temp_selected_hero
        self.game_instance.selected_hero = self.selected_hero  # ✅ Store hero in game instance
        self.confirmation_active = False

        # Visual feedback - show selected hero for 3 seconds
        self.selection_time = time.time()

        # Force the screen to freeze properly for 3 seconds
        freeze_duration = 0
        start_time = time.time()
        while time.time() - start_time < freeze_duration:
            self.draw()
            pygame.display.update()

        # Select the hero's OST based on selection
        hero_ost_path = os.path.join(self.game_instance.script_dir, "assets", "audio", "ost", self.selected_hero, f"{self.selected_hero}_map_ost.mp3")

        # Proceed after freeze
        print(f"Loading map with {self.selected_hero.upper()} as the hero!")
        self.selection_time = None
        self.visible = False

        for button in self.buttons.values():
            button.active = True

        # Call the map function
        self.game_instance.map(hero_ost_path)

    def cancel_hero_selection(self):
        """User cancelled hero selection with 'No' button."""
        print(f"Hero {self.temp_selected_hero.upper()} selection cancelled.")
        self.confirmation_active = False
        self.temp_selected_hero = None

        # Reset button states and make them active again
        for button in self.buttons.values():
            button.image = button.idle_img
            button.active = True

    def update(self, event):
        """Handles button interactions and enforces click delay."""
        if self.visible:
            if event.type == CONFIRMATION_DELAY:
                # Show confirmation exactly after 1 second
                self.confirmation_active = True
                pygame.time.set_timer(CONFIRMATION_DELAY, 0)  # Stop the timer

            if self.confirmation_active:
                # While confirmation is active, only Yes/No buttons respond
                self.yes_button.update(event)
                self.no_button.update(event)
            else:
                # Normal hero selection state
                for button in self.buttons.values():
                    button.update(event)
                self.back_button.update(event)

    def draw(self):
        """Draw the hero selection screen."""
        frame_surface = self.background_menu.get_frame()
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(frame_surface, (0, 0))

        if self.visible:
            # Draw the main border
            self.screen.blit(self.border_img, self.border_rect.topleft)

            # Draw all hero buttons
            for button in self.buttons.values():
                button.draw(self.screen)

            # If confirmation dialog is active, draw it over everything else
            if self.confirmation_active:
                self.screen.blit(self.confirmation_border, self.confirmation_border_rect.topleft)

                # Draw Yes/No buttons
                self.yes_button.draw(self.screen)
                self.no_button.draw(self.screen)
            else:
                # Draw back button only when confirmation is not showing
                self.back_button.draw()

        pygame.display.update()

    def show(self):
        """Show the hero selection screen."""
        self.visible = True
        self.selected_hero = None
        self.temp_selected_hero = None
        self.confirmation_active = False
        self.selection_time = None
        for button in self.buttons.values():
            button.visible = True
            button.active = True
        print("Hero selection screen opened.")

    def hide(self):
        """Hide the hero selection screen."""
        self.visible = False
        self.confirmation_active = False
        if self.voiceline_sound:
            self.voiceline_sound.stop()
            self.voiceline_sound = None
        print("Hero selection screen closed.")

    def go_back(self):
        """Handles Back button click."""
        print("Back button clicked!")
        self.hide()
        if self.game_instance:
            self.game_instance.game_modes.show()