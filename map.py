import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from back_button import BackButton

class Map:
    def __init__(self, screen, script_dir, go_back_callback):
        """Initialize the LSPU map with a Back button."""
        self.screen = screen
        self.running = True
        self.dragging = False
        self.last_mouse_x, self.last_mouse_y = 0, 0
        self.go_back_callback = go_back_callback  # Store the callback function

        # Load and scale the map
        self.map_original = pygame.image.load("images/map/lspu_map.png")
        SCALE_FACTOR = 1.5
        self.map_width = int(self.map_original.get_width() * SCALE_FACTOR)
        self.map_height = int(self.map_original.get_height() * SCALE_FACTOR)
        self.map = pygame.transform.scale(self.map_original, (self.map_width, self.map_height))

        # Initial map position
        self.map_x, self.map_y = 0, 0

        # Initialize the Back button
        self.back_button = BackButton(screen, script_dir, self.go_back, position=(100, 100), scale=0.25)

    def go_back(self):
        """Handle back button action."""
        if self.go_back_callback:
            self.go_back_callback()  # Call the callback to return to the main menu
        self.running = False  # Stop the map loop

    def draw(self):
        """Draw the map and the Back button on the screen."""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.map, (self.map_x, self.map_y))
        self.back_button.draw()
        pygame.display.update()

    def handle_events(self):
        """Handle map interactions like dragging and back button."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.back_button.update(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.dragging = True
                self.last_mouse_x, self.last_mouse_y = event.pos

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx = event.pos[0] - self.last_mouse_x
                dy = event.pos[1] - self.last_mouse_y
                self.map_x += dx
                self.map_y += dy
                self.last_mouse_x, self.last_mouse_y = event.pos
                self.map_x = max(min(0, self.map_x), SCREEN_WIDTH - self.map_width)
                self.map_y = max(min(0, self.map_y), SCREEN_HEIGHT - self.map_height)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False