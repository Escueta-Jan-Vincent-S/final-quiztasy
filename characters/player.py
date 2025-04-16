import pygame
import os
from settings import FONT_PATH

class Player:
    def __init__(self, script_dir, player_type="boy"):
        self.script_dir = script_dir
        self.player_type = player_type
        self.hp = 10  # Universal HP for every level
        self.max_hp = 10

        # Load player image based on type (boy or girl)
        image_path = os.path.join(script_dir, "assets", "images", "battle", self.player_type, f"{self.player_type}_stand.png")
        self.image = pygame.image.load(image_path)

        # Scale image if needed (adjust scale factor as appropriate)
        scale_factor = 5  # Adjust this value based on your image size
        self.image = pygame.transform.scale(self.image,(int(self.image.get_width() * scale_factor),int(self.image.get_height() * scale_factor)))

        # Position the player on the left side of the screen
        self.rect = self.image.get_rect()
        self.rect.x = 300  # Left side position
        self.rect.bottom = 700  # Adjust this value as needed

    def take_damage(self, amount):
        """Applies damage to the player"""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        return self.hp <= 0  # Returns True if player is defeated

    def heal(self, amount):
        """Heals the player by the specified amount"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def draw(self, screen):
        """Draws the player on the screen"""
        screen.blit(self.image, self.rect)

        # Draw HP bar
        bar_width = 200
        bar_height = 20
        bar_x = 100
        bar_y = screen.get_height() - bar_height - 320

        # Background (empty) bar
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Filled portion of the bar
        health_width = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

        # HP text
        font = pygame.font.Font(FONT_PATH, 20)
        hp_text = font.render(f"{self.hp}/{self.max_hp} HP", True, (255, 255, 255))
        screen.blit(hp_text, (bar_x + 10, bar_y + 2))