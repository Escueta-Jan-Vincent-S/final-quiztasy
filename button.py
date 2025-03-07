import pygame

class Button:
    def __init__(self, x, y, idle_img, hover_img, click_img=None, action=None, scale=1.0, audio_manager=None):
        """Creates a button with idle, hover, and click states."""
        # Load images if they are file paths (strings), otherwise assume they are already loaded surfaces
        self.idle_img = self.load_image(idle_img)
        self.hover_img = self.load_image(hover_img)

        # If no click image is provided, use the hover image
        if click_img:
            self.click_img = self.load_image(click_img)
        else:
            self.click_img = self.hover_img  # Fallback to hover image

        # Scale images if needed
        self.idle_img = pygame.transform.scale(self.idle_img, (
            int(self.idle_img.get_width() * scale), int(self.idle_img.get_height() * scale)))
        self.hover_img = pygame.transform.scale(self.hover_img, (
            int(self.hover_img.get_width() * scale), int(self.hover_img.get_height() * scale)))
        self.click_img = pygame.transform.scale(self.click_img, (
            int(self.click_img.get_width() * scale), int(self.click_img.get_height() * scale)))

        self.image = self.idle_img
        self.rect = self.image.get_rect(center=(x, y))
        self.action = action  # Function to call when clicked
        self.visible = True
        self.active = True
        self.clicked = False

        # Store audio manager instead of directly storing the sound
        self.audio_manager = audio_manager

    def load_image(self, img):
        """Helper method to load an image if it's a file path, or return it directly if it's already a surface."""
        if isinstance(img, str):  # If it's a file path
            return pygame.image.load(img).convert_alpha()
        return img  # If it's already a pygame.Surface

    def draw(self, screen):
        """Draws the button on the screen."""
        if self.visible:
            screen.blit(self.image, self.rect.topleft)

    def update(self, event):
        """Handles hover and click effects, accepts Pygame events."""
        if self.visible and self.active:
            mouse_pos = pygame.mouse.get_pos()

            # Hover effect
            if self.rect.collidepoint(mouse_pos):
                self.image = self.hover_img
            else:
                self.image = self.idle_img

            # Click effect - Detect mouse button release
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
                self.image = self.click_img
                self.clicked = True  # Mouse is being pressed down

            elif event.type == pygame.MOUSEBUTTONUP and self.clicked:
                self.clicked = False  # Click action is finished

                # ✅ Ensure sound only plays if `audio_manager.audio_enabled` is True
                if self.audio_manager and self.audio_manager.audio_enabled:
                    self.audio_manager.play_sfx()

                if self.action:
                    self.action()  # Call the button's assigned function