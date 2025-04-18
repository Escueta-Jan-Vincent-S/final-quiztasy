import pygame
import random
import time
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH


class CoinToss:
    def __init__(self, screen, script_dir, audio_manager=None, battle_instance=None):
        """Initialize the coin toss screen."""
        self.screen = screen
        self.script_dir = script_dir
        self.audio_manager = audio_manager
        self.battle_instance = battle_instance  # Store reference to battle instance
        self.font = pygame.font.Font(FONT_PATH, 50)
        self.result_font = pygame.font.Font(FONT_PATH, 60)
        self.small_font = pygame.font.Font(FONT_PATH, 30)

        # Overlay for darkening the background
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(180)  # Set transparency (0-255)

        # Load coin images
        self.heads_img = pygame.image.load(os.path.join(script_dir, "assets", "images", "coin", "heads.png"))
        self.tails_img = pygame.image.load(os.path.join(script_dir, "assets", "images", "coin", "tails.png"))

        # Scale coin images
        scale_factor = 0.5
        self.heads_img = pygame.transform.scale(self.heads_img,(int(self.heads_img.get_width() * scale_factor),int(self.heads_img.get_height() * scale_factor)))
        self.tails_img = pygame.transform.scale(self.tails_img,(int(self.tails_img.get_width() * scale_factor),int(self.tails_img.get_height() * scale_factor)))

        # Load coin flip sound
        self.coin_flip_sound = pygame.mixer.Sound(os.path.join(script_dir, "assets", "audio", "sfx", "coin_flip.mp3"))

        # Button areas
        self.heads_button = pygame.Rect(SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2 + 100, 275, 80)
        self.tails_button = pygame.Rect(3 * SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2 + 100, 275, 80)

        # State variables
        self.player1_choice = None
        self.toss_result = None
        self.animation_running = False
        self.animation_start_time = 0
        self.first_player = None
        self.toss_complete = False
        self.current_coin_img = self.heads_img
        self.flip_count = 0
        self.max_flips = 10
        self.last_flip_time = 0
        self.flip_delay = 0.1  # seconds between flips

    def handle_events(self, event):
        """Handle user input during coin toss."""
        if event.type == pygame.MOUSEBUTTONDOWN and not self.animation_running and self.player1_choice is None:
            mouse_pos = pygame.mouse.get_pos()

            # Check if heads button was clicked
            if self.heads_button.collidepoint(mouse_pos):
                self.player1_choice = "heads"
                self.start_coin_animation()

            # Check if tails button was clicked
            elif self.tails_button.collidepoint(mouse_pos):
                self.player1_choice = "tails"
                self.start_coin_animation()

    def start_coin_animation(self):
        """Start the coin flip animation."""
        if self.audio_manager and self.audio_manager.audio_enabled:
            self.coin_flip_sound.play()

        self.animation_running = True
        self.animation_start_time = time.time()
        self.flip_count = 0
        self.last_flip_time = time.time()

        # Determine the actual result
        self.toss_result = random.choice(["heads", "tails"])

    def update(self):
        """Update the coin toss animation."""
        if self.animation_running:
            current_time = time.time()

            # Check if we should flip the coin
            if current_time - self.last_flip_time > self.flip_delay:
                self.flip_count += 1
                self.last_flip_time = current_time

                # Switch between heads and tails
                if self.current_coin_img == self.heads_img:
                    self.current_coin_img = self.tails_img
                else:
                    self.current_coin_img = self.heads_img

            # End animation after max flips
            if self.flip_count >= self.max_flips:
                self.animation_running = False
                self.toss_complete = True

                # Set the final image to match the result
                self.current_coin_img = self.heads_img if self.toss_result == "heads" else self.tails_img

                # Determine first player
                if self.player1_choice == self.toss_result:
                    self.first_player = 1
                else:
                    self.first_player = 2

    def draw(self):
        """Draw the coin toss screen."""
        # Draw the battle screen in the background first if battle instance exists
        if self.battle_instance:
            self.battle_instance.draw_background_for_coin_toss()
            # Apply darkening overlay
            self.screen.blit(self.overlay, (0, 0))
        else:
            # Fall back to black background if no battle instance
            self.screen.fill((0, 0, 0))

        # Draw title
        title_text = self.font.render("Coin Toss", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Draw instruction
        if not self.player1_choice:
            instruction_text = self.font.render("Player 1: Choose Heads or Tails", True, (255, 255, 0))
        else:
            instruction_text = self.font.render(f"Player 1 chose {self.player1_choice.upper()}", True, (255, 255, 0))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(instruction_text, instruction_rect)

        # Draw coin
        coin_rect = self.current_coin_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(self.current_coin_img, coin_rect)

        # Draw buttons if choice not yet made
        if not self.player1_choice:
            # Heads button
            pygame.draw.rect(self.screen, (50, 50, 200), self.heads_button)
            pygame.draw.rect(self.screen, (255, 255, 255), self.heads_button, 2)
            heads_text = self.font.render("HEADS", True, (255, 255, 255))
            heads_text_rect = heads_text.get_rect(center=self.heads_button.center)
            self.screen.blit(heads_text, heads_text_rect)

            # Tails button
            pygame.draw.rect(self.screen, (200, 50, 50), self.tails_button)
            pygame.draw.rect(self.screen, (255, 255, 255), self.tails_button, 2)
            tails_text = self.font.render("TAILS", True, (255, 255, 255))
            tails_text_rect = tails_text.get_rect(center=self.tails_button.center)
            self.screen.blit(tails_text, tails_text_rect)

        # Draw result text if toss is complete
        if self.toss_complete:
            result_text = self.result_font.render(f"{self.toss_result.upper()}!", True, (255, 215, 0))
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
            self.screen.blit(result_text, result_rect)

            # Show who goes first
            first_player_text = self.font.render(f"Player {self.first_player} goes first!", True, (0, 255, 0))
            first_player_rect = first_player_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 220))
            self.screen.blit(first_player_text, first_player_rect)

            # Show "Press any key to continue" message
            continue_text = self.small_font.render("Press any key to continue...", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(continue_text, continue_rect)

    def run(self):
        """Run the coin toss and return the player who goes first."""
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if self.toss_complete and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                    running = False

                self.handle_events(event)

            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        return self.first_player