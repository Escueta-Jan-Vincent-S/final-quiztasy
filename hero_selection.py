import pygame
import os
import time
import random
from button import Button
from back_button import BackButton
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class HeroSelection:
    def __init__(self, game_instance, background_menu):
        """Initialize Hero Selection screen with character choices."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.visible = False  # Hero selection starts hidden
        self.background_menu = background_menu
        self.audio_manager = game_instance.audio_manager

        # Load background border
        border_path = os.path.join(game_instance.script_dir, "images", "buttons", "game modes", "hero selection",
                                   "choose_hero_border.png")
        self.border_img = pygame.image.load(border_path)
        self.border_rect = self.border_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Character button positions
        self.positions = {
            "boy": (self.border_rect.centerx - 300, self.border_rect.centery + 30),
            "girl": (self.border_rect.centerx + 300, self.border_rect.centery + 30)
        }

        # Load character buttons with scaling
        self.buttons = {
            "boy": self.create_button("boy", self.positions["boy"], scale=0.7, freeze_duration = 1),
            "girl": self.create_button("girl", self.positions["girl"], scale=0.7, freeze_duration = 1)
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
                os.path.join(game_instance.script_dir, "audio", "voiceline", "boy", "hero selection", f"boy_voice_{i}.mp3") for i in range(1, 4)
            ],
            "girl": [
                os.path.join(game_instance.script_dir, "audio", "voiceline", "girl", "hero selection", f"girl_voice_{i}.mp3") for i in range(1, 4)
            ]
        }

        self.selected_hero = None
        self.selection_time = None
        self.voiceline_sound = None

    def create_button(self, name, position, scale=1.0, freeze_duration=0):
        """Helper to create buttons with optional freeze duration."""
        base_path = os.path.join(self.game_instance.script_dir, "images", "buttons", "game modes", "hero selection")
        return Button(
            position[0], position[1],
            os.path.join(base_path, f"{name}_hero_border_img.png"),
            os.path.join(base_path, f"{name}_hero_border_hover.png"),
            os.path.join(base_path, f"{name}_hero_border_click.png"),
            lambda: self.select_hero(name),
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

    def select_hero(self, hero):
        """Handles character selection and respects audio settings."""
        if self.selection_time is None:
            print(f"Hero {hero.upper()} selected!")
            self.selected_hero = hero
            self.selection_time = time.time()
            # 🔊 Only play voiceline if audio is enabled
            self.play_random_voiceline(hero)
            for button in self.buttons.values():
                button.active = False
            self.buttons[hero].current_image = self.buttons[hero].click_img
            self.draw()
            pygame.display.update()

    def update(self, event):
        """Handles button interactions and enforces click delay."""
        if self.visible:
            if self.selection_time is None:
                for button in self.buttons.values():
                    button.update(event)
                self.back_button.update(event)
            else:
                if time.time() - self.selection_time >= 1:
                    print(f"Confirmed {self.selected_hero.upper()} as the hero!")
                    self.selection_time = None
                    self.visible = False

                    for button in self.buttons.values():
                        button.active = True

    def draw(self):
        """Draw the hero selection screen."""
        frame_surface = self.background_menu.get_frame()
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(frame_surface, (0, 0))

        if self.visible:
            self.screen.blit(self.border_img, self.border_rect.topleft)

            if self.selected_hero:
                self.buttons[self.selected_hero].current_image = self.buttons[self.selected_hero].click_img

            for button in self.buttons.values():
                button.draw(self.screen)

            self.back_button.draw()

        pygame.display.update()

    def show(self):
        """Show the hero selection screen."""
        self.visible = True
        self.selected_hero = None
        self.selection_time = None
        for button in self.buttons.values():
            button.visible = True
            button.active = True
        print("Hero selection screen opened.")

    def hide(self):
        """Hide the hero selection screen."""
        self.visible = False
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