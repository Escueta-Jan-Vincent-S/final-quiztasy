import pygame
import time

class Button:
    def __init__(self, x, y, idle_img, hover_img, click_img=None, action=None, scale=1.0, audio_manager=None, freeze_duration=0):
        """Creates a button with optional freeze time (only for Hero Selection buttons)."""
        self.idle_img = self.load_image(idle_img)
        self.hover_img = self.load_image(hover_img)
        self.click_img = self.load_image(click_img) if click_img else self.hover_img

        # Scale images
        self.idle_img = pygame.transform.scale(self.idle_img, (int(self.idle_img.get_width() * scale), int(self.idle_img.get_height() * scale)))
        self.hover_img = pygame.transform.scale(self.hover_img, (int(self.hover_img.get_width() * scale), int(self.hover_img.get_height() * scale)))
        self.click_img = pygame.transform.scale(self.click_img, (int(self.click_img.get_width() * scale), int(self.click_img.get_height() * scale)))

        self.image = self.idle_img
        self.rect = self.image.get_rect(center=(x, y))
        self.action = action
        self.visible = True
        self.active = True
        self.clicked = False
        self.click_time = None  # Track click time
        self.freeze_duration = freeze_duration  # ❗ Only Hero Selection buttons will have a freeze time

        self.audio_manager = audio_manager

    def load_image(self, img):
        """Helper method to load an image from file or return the surface if already loaded."""
        return pygame.image.load(img).convert_alpha() if isinstance(img, str) else img

    def draw(self, screen):
        """Draw the button on the screen."""
        if self.visible:
            screen.blit(self.image, self.rect.topleft)

    def update(self, event):
        """Handles hover, click, and optional freeze effect for Hero Selection."""
        if not self.visible or not self.active:
            return  # Ignore updates if the button is disabled

        mouse_pos = pygame.mouse.get_pos()

        # If button has a freeze duration, stay on click_img
        if self.clicked and self.freeze_duration > 0:
            if time.time() - self.click_time >= self.freeze_duration:  # Wait for freeze_duration seconds
                self.clicked = False
                self.image = self.idle_img  # Return to normal
            return  # Skip hover effect while frozen

        # Hover effect
        if self.rect.collidepoint(mouse_pos):
            self.image = self.hover_img
        else:
            self.image = self.idle_img

        # Click effect
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.image = self.click_img
            self.clicked = True
            self.click_time = time.time()  # Start freeze timer

            if self.audio_manager and self.audio_manager.audio_enabled:
                self.audio_manager.play_sfx()

            if self.action:
                self.action()  # Call the assigned function
