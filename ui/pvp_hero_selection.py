import pygame
import os
import time
import random
from ui.button import Button
from .back_button import BackButton
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

CONFIRMATION_DELAY = pygame.USEREVENT + 1

class PVPHeroSelection:
    def __init__(self, game_instance, background_menu):
        """Initialize PVP Hero Selection screen with character choices for both players."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.visible = False  # Hero selection starts hidden
        self.background_menu = background_menu
        self.audio_manager = game_instance.audio_manager

        # Player turn tracking
        self.current_player = 1  # Start with Player 1
        self.selected_heroes = {1: None, 2: None}  # Store selections for both players

        # Load player selection borders
        border_path_p1 = os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "player1_selection_border.png")
        border_path_p2 = os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "player2_selection_border.png")

        # Load and scale player selection borders
        border_scale = 0.85  # Adjust as needed
        original_border_p1 = pygame.image.load(border_path_p1)
        original_border_p2 = pygame.image.load(border_path_p2)

        border_width_p1 = int(original_border_p1.get_width() * border_scale)
        border_height_p1 = int(original_border_p1.get_height() * border_scale)
        self.border_img_p1 = pygame.transform.scale(original_border_p1, (border_width_p1, border_height_p1))

        border_width_p2 = int(original_border_p2.get_width() * border_scale)
        border_height_p2 = int(original_border_p2.get_height() * border_scale)
        self.border_img_p2 = pygame.transform.scale(original_border_p2, (border_width_p2, border_height_p2))

        # Position borders
        self.border_rect_p1 = self.border_img_p1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.border_rect_p2 = self.border_img_p2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        # Character button positions for player 1
        self.positions_p1 = {
            "boy": (self.border_rect_p1.centerx - 300, self.border_rect_p1.centery + 87),
            "girl": (self.border_rect_p1.centerx + 300, self.border_rect_p1.centery + 87)
        }

        self.positions_p2 = {
            "boy": (self.border_rect_p1.centerx - 300, self.border_rect_p1.centery + 87),
            "girl": (self.border_rect_p1.centerx + 300, self.border_rect_p1.centery + 87)
        }

        # Load character buttons with scaling for both players
        self.buttons_p1 = {
            "boy": self.create_button("boy", self.positions_p1["boy"], 1, scale=0.7, freeze_duration=1),
            "girl": self.create_button("girl", self.positions_p1["girl"], 1, scale=0.7, freeze_duration=1)
        }

        self.buttons_p2 = {
            "boy": self.create_button("boy", self.positions_p2["boy"], 2, scale=0.7, freeze_duration=1),
            "girl": self.create_button("girl", self.positions_p2["girl"], 2, scale=0.7, freeze_duration=1)
        }

        # Initially disable Player 2 buttons until Player 1 has chosen
        for button in self.buttons_p2.values():
            button.active = False

        # Add Back button
        self.back_button = BackButton(
            self.screen,
            self.game_instance.script_dir,
            self.go_back,
            audio_manager=self.game_instance.audio_manager,
            position=(100, 100),
            scale=0.25
        )

        # Load hero voicelines - same as in hero_selection.py
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
        self.temp_player = None

        # Load confirmation border with scaling
        confirmation_border_path = os.path.join(game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection", "yes_or_no_border.png")
        self.confirmation_border_original = pygame.image.load(confirmation_border_path)

        # Apply scaling to confirmation border
        border_scale = 0.7
        border_width = int(self.confirmation_border_original.get_width() * border_scale)
        border_height = int(self.confirmation_border_original.get_height() * border_scale)
        self.confirmation_border = pygame.transform.scale(self.confirmation_border_original,
                                                          (border_width, border_height))
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

        self.selection_time = None
        self.voiceline_sound = None

        # Status text for player turn indication
        self.font = pygame.font.Font(None, 48)
        self.status_text = self.font.render("Player 1's Turn", True, (255, 255, 255))
        self.status_rect = self.status_text.get_rect(center=(SCREEN_WIDTH // 2, 150))

    def create_button(self, name, position, player, scale=1.0, freeze_duration=0):
        """Helper to create buttons with player number."""
        base_path = os.path.join(self.game_instance.script_dir, "assets", "images", "buttons", "game modes", "hero selection")
        return Button(
            position[0], position[1],
            os.path.join(base_path, f"{name}_hero_border_img.png"),
            os.path.join(base_path, f"{name}_hero_border_hover.png"),
            os.path.join(base_path, f"{name}_hero_border_click.png"),
            lambda hero=name, p=player: self.pre_select_hero(hero, p),
            scale=scale,
            audio_manager=self.game_instance.audio_manager,
            freeze_duration=freeze_duration
        )

    def play_random_voiceline(self, hero):
        """Play a random voiceline for the selected hero if audio is enabled."""
        if not self.audio_manager.audio_enabled:
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

    def pre_select_hero(self, hero, player):
        """Initial hero selection that starts confirmation."""
        print(f"Player {player} pre-selecting hero: {hero.upper()}")

        # Play hero voiceline immediately
        self.play_random_voiceline(hero)

        # Set the button to "clicked" image
        buttons_dict = self.buttons_p1 if player == 1 else self.buttons_p2
        for button_name, button in buttons_dict.items():
            if button_name == hero:
                button.image = button.click_img
            else:
                button.image = button.idle_img

        # Disable all buttons while waiting
        for button in self.buttons_p1.values():
            button.active = False
        for button in self.buttons_p2.values():
            button.active = False

        # Start a 1-second timer for confirmation
        self.temp_selected_hero = hero
        self.temp_player = player
        pygame.time.set_timer(CONFIRMATION_DELAY, 1000, loops=1)  # Trigger event after 1s

    def confirm_hero_selection(self):
        """User confirmed hero selection with 'Yes' button."""
        print(f"Player {self.temp_player} selected {self.temp_selected_hero.upper()}!")

        # Store the selection
        self.selected_heroes[self.temp_player] = self.temp_selected_hero

        # Reset confirmation state
        self.confirmation_active = False

        # If it was Player 1, move to Player 2
        if self.temp_player == 1:
            self.current_player = 2
            # Enable Player 2 buttons
            for button in self.buttons_p2.values():
                button.active = True
            # Update status text
            self.status_text = self.font.render("Player 2's Turn", True, (255, 255, 255))
            self.status_rect = self.status_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        else:  # Both players have selected
            # Store selections in game instance
            self.game_instance.p1_hero = self.selected_heroes[1]
            self.game_instance.p2_hero = self.selected_heroes[2]

            print(f"PVP match setup: Player 1 ({self.selected_heroes[1]}) vs Player 2 ({self.selected_heroes[2]})")

            # Add a small delay to see the selection
            self.selection_time = time.time()
            freeze_duration = 1  # Short delay to see the final selection
            start_time = time.time()
            while time.time() - start_time < freeze_duration:
                self.draw()
                pygame.display.update()

            # Hide this screen
            self.hide()

            # Start the PVP battle directly instead of returning to game_modes
            if self.game_instance and hasattr(self.game_instance, 'pvp'):
                # Initialize PVP battle with the currently selected level
                self.game_instance.pvp.start_battle()
            else:
                print("Error: PVP module not found in game instance")
                # Fallback to game_modes if pvp is not initialized
                if hasattr(self.game_instance, 'game_modes'):
                    self.game_instance.game_modes.show()

    def cancel_hero_selection(self):
        """User cancelled hero selection with 'No' button."""
        print(f"Player {self.temp_player} cancelled {self.temp_selected_hero.upper()} selection.")
        self.confirmation_active = False
        self.temp_selected_hero = None

        # Re-enable appropriate buttons based on current player
        if self.current_player == 1:
            for button in self.buttons_p1.values():
                button.image = button.idle_img
                button.active = True
        else:
            for button in self.buttons_p2.values():
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
                # Normal hero selection state based on current player
                if self.current_player == 1:
                    for button in self.buttons_p1.values():
                        button.update(event)
                else:
                    for button in self.buttons_p2.values():
                        button.update(event)
                self.back_button.update(event)

    def draw(self):
        """Draw the PVP hero selection screen."""
        frame_surface = self.background_menu.get_frame()
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(frame_surface, (0, 0))

        if self.visible:
            # Draw the status text showing whose turn it is
            self.screen.blit(self.status_text, self.status_rect)

            # Only draw Player 1's border and buttons if it's Player 1's turn
            if self.current_player == 1:
                self.screen.blit(self.border_img_p1, self.border_rect_p1.topleft)
                for button in self.buttons_p1.values():
                    button.draw(self.screen)
            # Only draw Player 2's border and buttons if it's Player 2's turn
            elif self.current_player == 2:
                self.screen.blit(self.border_img_p2, self.border_rect_p2.topleft)
                for button in self.buttons_p2.values():
                    button.draw(self.screen)

            # If confirmation dialog is active, draw it over everything else
            if self.confirmation_active:
                self.screen.blit(self.confirmation_border, self.confirmation_border_rect.topleft)
                self.yes_button.draw(self.screen)
                self.no_button.draw(self.screen)
            else:
                # Draw back button only when confirmation is not showing
                self.back_button.draw()

        pygame.display.update()

    def show(self):
        """Show the PVP hero selection screen."""
        self.visible = True
        self.current_player = 1  # Reset to Player 1
        self.selected_heroes = {1: None, 2: None}  # Clear previous selections
        self.confirmation_active = False
        self.selection_time = None

        # Enable Player 1 buttons, disable Player 2
        for button in self.buttons_p1.values():
            button.visible = True
            button.active = True
            button.image = button.idle_img

        for button in self.buttons_p2.values():
            button.visible = True
            button.active = False
            button.image = button.idle_img

        print("PVP Hero selection screen opened.")

    def hide(self):
        """Hide the hero selection screen."""
        self.visible = False
        self.confirmation_active = False
        if self.voiceline_sound:
            self.voiceline_sound.stop()
            self.voiceline_sound = None
        print("PVP Hero selection screen closed.")

    def go_back(self):
        """Handles Back button click."""
        print("Back button clicked!")
        self.hide()
        if self.game_instance:
            self.game_instance.game_modes.show()