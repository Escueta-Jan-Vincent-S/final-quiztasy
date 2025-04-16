import pygame
import os

# Initialize Pygame
pygame.init()

# ================================
# 🛠️ GAME SETTINGS
# ================================

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Font settings
FONT_PATH = os.path.join("assets", "fonts", "press_start_2p.ttf")
FONT_SIZE = 24

# Load font
game_font = pygame.font.Font(FONT_PATH, FONT_SIZE)